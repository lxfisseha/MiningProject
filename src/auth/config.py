from pydantic_settings import BaseSettings
from src.config import settings

class AuthSettings(BaseSettings):
    JWT_SECRET_KEY: str = settings.JWT_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    

settings = AuthSettings()