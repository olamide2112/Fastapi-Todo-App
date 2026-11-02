import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL")

# Use the local SQLite database by default. Set DATABASE_URL when deploying
# with PostgreSQL or another supported SQLAlchemy database.
SQLALCHEMY_DATABASE_URL = DATABASE_URL or f"sqlite:///{(BASE_DIR / 'todosapp.db').as_posix()}"

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
Base = declarative_base()

SessionLocal = sessionmaker(autocommit= False, autoflush= False, bind= engine)

