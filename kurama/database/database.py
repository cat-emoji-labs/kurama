from pymongo import MongoClient
from kurama.config.environment import DB_URL


class NLPDatabase:
    def __init__(self):
        self.client = MongoClient(DB_URL)
        self.db = self.client["database"]
