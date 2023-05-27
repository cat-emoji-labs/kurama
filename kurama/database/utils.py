from kurama.model.model import ask_model_with_retry
from kurama.model.prompt import type_inference_prompt, pipeline_prompt, schema_prompt
from kurama.config.constants import DEFAULT_AST_ALLOWED_TYPES
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


def retrieve_best_collection_name(schemas: str, query: str) -> str:
    """
    (LLM function)
    Uses LLM as a router to retrieve the collection that best matches the query.
    """
    prompt = schema_prompt.format(schemas=schemas, query=query)
    res = ask_model_with_retry(prompt=prompt)
    return res


def upload_csv(csv: BinaryIO, collection: Collection) -> None:
    """
    Uploads a CSV file to a supplied MongoDB collection.
    Includes type-inference via LLM.
    """
    df = pd.read_csv(csv)
    # Replace NaN values
    df = df.where(pd.notnull(df), None)
    columns = df.columns.tolist()
    first_row = df.iloc[0]
    types = _build_types_array(columns=columns, first_row=first_row)
    for _, row in df.iterrows():
        try:
            transformed_row = _transform_row(types, row.values.tolist())
            document = dict(zip(columns, transformed_row))
            collection.insert_one(document=document)
        except Exception as e:
            # Discard rows that don't conform to the type
            # TODO: Display discarded rows to the user
            print(e, row.values.tolist())
