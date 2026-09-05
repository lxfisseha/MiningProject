from sqlmodel import create_engine, Session
from fastapi import Depends
from typing import Annotated

from .config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)


def get_session():
    with Session(engine) as session:
        yield session


SESSION_DEP = Annotated[Session, Depends(get_session)]
