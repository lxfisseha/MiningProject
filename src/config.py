from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl


class EnvSettings(BaseSettings):
    model_config = {
            "env_file": ".env"
        }
    
    DATABASE_URL: str = Field(...)
    CSRF_SECRET_KEY: str = Field(..., min_length=10)
    JWT_SECRET_KEY: str = Field(...)

settings = EnvSettings()