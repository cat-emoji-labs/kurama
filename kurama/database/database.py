from pymongo import MongoClient
from kurama.config.environment import DB_URL


class NLPDatabase:
    def __init__(self):
        self.client = MongoClient(DB_URL)

    def _get_db_for_user(self, user_id):
        return self.client[user_id]

    def get_collections(self, user_id):
        db = self._get_db_for_user(user_id)
        return db.list_collection_names()

    def get_collection(self, user_id, collection_id):
        db = self._get_db_for_user(user_id)
        return db.get_collection(collection_id)

    def get_collection_schema(self, user_id, collection_id):
        collection = self.get_collection(user_id, collection_id)
        return collection.find_one()
