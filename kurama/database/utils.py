from kurama.model.model import ask_model_with_retry
from kurama.model.prompt import *
from kurama.config.constants import DEFAULT_AST_ALLOWED_TYPES
from kurama.database.database import PostgresDatabase
import pandas as pd
import json
import ast
import datetime
from typing import List, BinaryIO
from pymongo.collection import Collection


def _transform_row(types: List[any], row: List[any]) -> List[any]:
    """
    Transforms a Pandas DataFrame row using a type array.
    Both input arrays must be the same dimension.
    """
    return list(
        map(
            lambda t, v: datetime.datetime.strptime(v, "%m/%d/%y %H:%M")
            if t == datetime.datetime.strptime and v
            else t(v),
            types,
            row,
        )
    )


def _is_allowed_types(node: ast.AST, allowed_types: tuple = DEFAULT_AST_ALLOWED_TYPES) -> bool:
    """
    Checks if an AST Node is in allowed_types OR is an instance of a datetime object.
    """
    return isinstance(
        node,
        (allowed_types),
    ) or (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "datetime"
    )


def _custom_eval(astr: str) -> any:
    """
    Parses raw LLM output, performs a walk on AST nodes for validation, and safely returns the result as a Python expression using the `eval()` function.
    """
    try:
        tree = ast.parse(astr)
    except SyntaxError:
        raise ValueError(astr)
    for node in ast.walk(tree):
        if not _is_allowed_types(node=node):
            raise ValueError(f"Invalid type ${node}-${ast.unparse(node)} in ${astr}")
    return eval(astr)


def _build_types_array(columns: List[str], first_row: List[str]) -> List[type]:
    """
    (LLM function)
    Builds an array of types using the columns and first row from a CSV file.
    """
    prompt = type_inference_prompt.format(columns=columns, row=first_row)
    res = ask_model_with_retry(prompt=prompt, func=json.loads)
    return [type(v) if v != "datetime" else datetime.datetime.strptime for v in res.values()]


def retrieve_pipeline_for_query(
    columns: List[str], query: str, date: datetime.datetime = datetime.datetime.today()
) -> any:
    """
    (LLM function)
    Retrieves a valid MongoDB pipeline using data columns, a user query, and a date (defaults to today).
    """
    prompt = pipeline_prompt.format(columns=columns, query=query, date=date)
    res = ask_model_with_retry(prompt=prompt, func=_custom_eval)
    return res


def _parse_sql_from_llm_out(llm_output: str):
    import re

    pattern = r"```(.*?)```"
    matches = re.findall(pattern, llm_output, re.DOTALL)
    return matches[-1].replace("SQL", "")  # only return the last SQL query


def _is_valid_sql(sql: str):
    import sqlparse

    parsed = sqlparse.parse(sql)
    if len(parsed) > 0:
        return sql
    else:
        raise ValueError("Invalid SQL statement")


# TODO: Move this function into database class
def get_sql_for_query(
    columns: List[str],
    query: str,
    pg: PostgresDatabase,
    date: datetime.datetime = datetime.datetime.today(),
):
    # Format the prompts
    prompt = sql_query_prompt.format(columns=columns, query=query)
    system_prompt = sql_system_prompt.format(date=date)

    # Get dataframe
    df = ask_model_with_retry(
        prompt=prompt,
        system_prompt=system_prompt,
        func=[_parse_sql_from_llm_out, _is_valid_sql, pg.execute],
        retry_prompt=retry_sql_query_prompt,
    )
    return df


def _get_sql_table_for_query(columns: List[str], first_row: List[str], name: str):
    prompt = sql_create_table_prompt.format(columns=columns, row=first_row, name=name)
    res = ask_model_with_retry(
        prompt=prompt,
        system_prompt=sql_create_table_system_prompt,
        func=[_parse_sql_from_llm_out, _is_valid_sql],
    )
    return res


# TODO: Move this function into database class
def retrieve_best_collection_name(schemas: str, query: str) -> str:
    """
    (LLM function)
    Uses LLM as a router to retrieve the collection that best matches the query.
    """
    prompt = schema_prompt.format(schemas=schemas, query=query)
    res = ask_model_with_retry(prompt=prompt)
    return res


# TODO: Move this function into database class
def upload_csv(csv: BinaryIO, name: str, collection: Collection, pg: PostgresDatabase) -> None:
    """
    Uploads a CSV file to a supplied MongoDB collection.
    Includes type-inference via LLM.
    """
    df = pd.read_csv(csv)
    # Replace NaN values
    df = df.where(pd.notnull(df), None)

    # Create the table
    columns = df.columns.tolist()
    first_row = df.iloc[0]
    create_table_statement = _get_sql_table_for_query(
        columns=columns, first_row=first_row, name=name
    )
    pg.create_table(sql=create_table_statement)

    # Get the table to insert into
    table = pg.get_table_by_name(table_name=name)

    # This takes way too long
    for _, row in df.iterrows():
        try:
            vals = tuple(row.values.tolist())
            pg.insert_into(table, vals)
        except Exception as e:
            # Discard rows that don't conform to the type
            # TODO: Display discarded rows to the user
            print("Couldn't insert: ", row.values.tolist())
