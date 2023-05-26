from kurama.model.model import ask_model_with_retry
from kurama.model.prompt import type_inference_prompt, pipeline_prompt
from kurama.config.constants import DEFAULT_AST_ALLOWED_TYPES
import pandas as pd
import json
import ast
import datetime
from typing import List
from fastapi import UploadFile
from pymongo.collection import Collection


def _transform_row(types: List[any], row: List[any]):
    return list(
        map(
            lambda t, v: datetime.datetime.strptime(v, "%m/%d/%y %H:%M")
            if t == datetime.datetime.strptime and v
            else t(v),
            types,
            row,
        )
    )


def _is_allowed_types(node: ast.AST, allowed_types: tuple = DEFAULT_AST_ALLOWED_TYPES):
    return isinstance(
        node,
        (allowed_types),
    ) or (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "datetime"
    )


def _custom_eval(astr: str):
    """
    Performs a walk on the AST
    Safely evaluates a string as a Python expression using the `eval()` function.

    Parameters:
    astr (str): A string containing a Python expression to evaluate.

    Returns:
    Any: The result of evaluating the expression.

    Raises:
    ValueError: If the input string contains any AST nodes that are not one of the allowed types.

    Assumptions/Limitations:
    - The input string must be a valid Python expression.
    - The allowed types for AST nodes are: `ast.Module`, `ast.Expr`, `ast.Dict`, `ast.Str`, `ast.Attribute`, `ast.Num`, `ast.Name`, `ast.Load`, `ast.Tuple`, `ast.List`, `ast.Call` (if the function being called is the `datetime` module).
    """
    try:
        tree = ast.parse(astr)
    except SyntaxError:
        raise ValueError(astr)
    for node in ast.walk(tree):
        if not _is_allowed_types(node=node):
            raise ValueError(f"Invalid type ${node}-${ast.unparse(node)} in ${astr}")
    return eval(astr)


def _build_types_array(columns: List[str], first_row: List[str]):
    prompt = type_inference_prompt.format(columns=columns, row=first_row)
    res = ask_model_with_retry(prompt=prompt, func=json.loads)
    return [type(v) if v != "datetime" else datetime.datetime.strptime for v in res.values()]


def retrieve_pipeline_for_query(columns: List[str], query: str, date: datetime.datetime):
    prompt = pipeline_prompt.format(columns=columns, query=query, date=date)
    res = ask_model_with_retry(prompt=prompt, func=_custom_eval)
    return res


def upload_csv(csv: UploadFile.file, collection: Collection):
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
