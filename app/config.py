from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str
    database_name: str 
    jwt_secret: str 
    jwt_algorithm: str  
    jwt_expires_s: int 

settings = Settings(mongodb_url="mongodb://43.225.26.120:27017/?directConnection=true",
                    database_name="user",
                    jwt_secret="45ea6cd85e28f7232534324045c2dbaafaa44c5c75fbe63278baa05f76c66441",
                    jwt_algorithm="HS256",
                    jwt_expires_s=3600
                    )