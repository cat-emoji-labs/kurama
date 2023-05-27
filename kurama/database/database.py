from pymongo import MongoClient
from pymongo.collection import Collection
from kurama.config.environment import DB_URL
from typing import List
import pandas as pd


class NLPDatabase:
    def __init__(self):
        self.client = MongoClient(DB_URL)

    def _get_db_for_user(self, user_id: str):
        return self.client[user_id]

    def get_collection_names(self, user_id: str):
        db = self._get_db_for_user(user_id)
        return db.list_collection_names()

    def get_collection(self, user_id: str, collection_id: str):
        db = self._get_db_for_user(user_id)
        return db.get_collection(collection_id)

    def get_collection_schema(self, user_id: str, collection_id: str):
        collection = self.get_collection(user_id, collection_id)
        res = collection.find_one()
        if res:
            return res.keys()
        # TODO: Return an error here

    def get_all_schemas(self, user_id):
        collection_names = self.get_collection_names(user_id=user_id)
        schema = ""
        for collection_name in collection_names:
            columns = self.get_collection_schema(user_id=user_id, collection_id=collection_name)
            schema += f"Collection name: {collection_name} Columns: {list(columns)}\n"
        return schema

    def execute_pipeline(self, pipeline: List[dict], collection: Collection):
        return pd.DataFrame(list(collection.aggregate(pipeline)))
