from sqlmodel import  create_engine, Session
from fastapi import Depends
from typing import Annotated

from pydantic_settings import BaseSettings
from pydantic import  AnyUrl
from .config import settings

class DBSettings(BaseSettings):
    DATABASE_URL: str = settings.DATABASE_URL
    echo: bool = False
    connect_args: dict = {"check_same_thread": False}

db_settings = DBSettings()

engine = create_engine(db_settings.DATABASE_URL, echo=db_settings.echo, connect_args=db_settings.connect_args)


def get_session():
    with Session(engine) as session:
        yield session


SESSION_DEP = Annotated[Session, Depends(get_session)]
