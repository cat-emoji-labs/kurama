from kurama.model.model import ask_model_with_retry
from kurama.model.prompt import type_inference_prompt, pipeline_prompt
import pandas as pd
import json
import ast


def transform_row(types, row):
    return list(map(lambda t, v: t(v) if v else None, types, row))


def build_types_array(columns, first_row):
    prompt = type_inference_prompt.format(columns=columns, row=first_row)
    res = ask_model_with_retry(prompt=prompt, func=json.loads)
    return [type(v) for v in res.values()]


def retrieve_pipeline_for_query(columns, query):
    prompt = pipeline_prompt.format(columns=columns, query=query)
    res = ask_model_with_retry(prompt=prompt, func=ast.literal_eval)
    return res


def upload_csv(csv, collection):
    df = pd.read_csv(csv)
    # Replace NaN values
    df = df.where(pd.notnull(df), None)
    columns = df.columns.tolist()
    first_row = df.iloc[0]
    types = build_types_array(columns=columns, first_row=first_row)
    for _, row in df.iterrows():
        try:
            transformed_row = transform_row(types, row.values.tolist())
            document = dict(zip(columns, transformed_row))
            collection.insert_one(document=document)
        except Exception as e:
            # Discard rows that don't conform to the type
            # TODO: Display discarded rows to the user
            print(e, row.values.tolist())
