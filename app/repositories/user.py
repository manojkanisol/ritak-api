from .base import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self.collection = self.db.users

    def find_by_email(self, email: str):
        return self.find_one({"email": email})
    
    def find_by_username(self, username: str):
        return self.find_one({"username": username})

    def create_user(self, user_data: dict):
        return self.insert_one(user_data)