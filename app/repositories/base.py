from typing import Any, Dict, List, Optional
from bson import ObjectId
from ..db.mongodb import mongodb

class BaseRepository:
    def __init__(self):
        self.db = mongodb.get_database()

    def find_one(self, query: Dict) -> Optional[Dict[str, Any]]:
        return self.collection.find_one(query)

    def find_many(self, query: Dict) -> List[Dict[str, Any]]:
        return list(self.collection.find(query))

    def insert_one(self, document: Dict) -> str:
        result = self.collection.insert_one(document)
        return str(result.inserted_id)