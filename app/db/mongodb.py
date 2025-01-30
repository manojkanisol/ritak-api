from pymongo import MongoClient
from ..config import settings

class MongoDB:
    def __init__(self):
        self.client = MongoClient(settings.mongodb_url)
        self.db = self.client[settings.database_name]

    def get_database(self):
        return self.db

mongodb = MongoDB()