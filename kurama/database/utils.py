from kurama.model.model import ask_model_with_retry
from kurama.model.prompt import *
from kurama.config.constants import DEFAULT_AST_ALLOWED_TYPES
from kurama.database.database import PostgresDatabase
import pandas as pd
import ast
import datetime
from typing import List, BinaryIO
import re


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


def _create_sql_table_for_csv(
    columns: List[str],
    first_row: List[str],
    table_name: str,
    pg: PostgresDatabase,
) -> None:
    prompt = sql_create_table_prompt.format(columns=columns, row=first_row, table_name=table_name)
    ask_model_with_retry(
        prompt=prompt,
        system_prompt=sql_create_table_system_prompt,
        func=[_parse_sql_from_llm_out, _is_valid_sql, pg.create_table],
        retry_prompt=retry_sql_query_prompt,
    )


def retrieve_df_for_query(
    query: str,
    pg: PostgresDatabase,
    user_id: str,
    date: datetime.datetime = datetime.datetime.today(),
):
    # Don't insert date unless necessary for query
    if re.search(r"(\d+)\s*(day|days|month|months)", query):
        date = f"Today's date is {date}."
    else:
        date = ""

    # Retrieve relevant columns and get schema name
    schema_name = get_schema_name_from_user_id(user_id=user_id)
    columns = pg.get_table_schemas(schema_name=schema_name)

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


def upload_csv(
    csv: BinaryIO, file_name: str, pg: PostgresDatabase, user_id: str, document_id: str
) -> None:
    """
    Uploads a CSV file to a supplied MongoDB collection.
    Includes type-inference via LLM.
    """

    df = pd.read_csv(csv)
    # Replace NaN values
    df = df.where(pd.notnull(df), None)

    # Get relevant schema name
    schema_name = get_schema_name_from_user_id(user_id=user_id)

    # Create the schema
    pg.create_schema_for_user_if_not_exists(schema_name=schema_name)

    # Create the table
    columns = df.columns.tolist()
    first_row = df.iloc[0]
    table_name = build_table_name(schema_name=schema_name, document_id=document_id)
    _create_sql_table_for_csv(columns=columns, first_row=first_row, table_name=table_name, pg=pg)

    # Get the table
    table = pg.get_table_by_name(table_name=table_name, schema_name=schema_name)

    # This takes way too long
    for _, row in df.iterrows():
        try:
            vals = tuple(row.values.tolist())
            pg.insert_into(table, vals)
        except Exception as e:
            # Discard rows that don't conform to the schema
            # TODO: Display discarded rows to the user
            print("Couldn't insert: ", row.values.tolist())


def delete_files(user_id: str, pg: PostgresDatabase, document_ids: List[str]) -> None:
    schema_name = get_schema_name_from_user_id(user_id=user_id)
    for document_id in document_ids:
        table_name = build_table_name(schema_name=schema_name, document_id=document_id)
        try:
            pg.drop_table(table_name=table_name)
        except Exception as e:
            print(f"Couldn't drop table {table_name}: {str(e)}")


def transpose_df(df: pd.DataFrame) -> List[object]:
    """
    Formats a Pandas DataFrame into an array of objects.
    """
    dict = df.head().to_dict()
    cols, rows = dict.keys(), [d.values() for d in dict.values()]
    res = []
    transposed_rows = [list(x) for x in zip(*rows)]
    for row in transposed_rows:
        obj = {}
        for col, val in zip(cols, row):
            obj[col] = val
        res.append(obj)
    return res


def get_schema_name_from_user_id(user_id: str) -> str:
    """
    Formats a raw user_id (UUID) into a Postgres-compatible schema name.
    """
    user_id = re.sub(r"-", "_", user_id)
    return f"schema_{user_id}"


def build_table_name(schema_name: str, document_id: str) -> str:
    """
    Formats a schema_name and document_id into a table_name
    """
    document_id = re.sub(r"-", "_", document_id)
    return f"{schema_name}.csv_{document_id}"
