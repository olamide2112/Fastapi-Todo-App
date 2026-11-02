# utils.py
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import pytest

from ..main import app
from ..database import Base
from ..models import Todos, Users
from ..routers.auth import bcrypt_context 

# Setup standard testing database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'codingwithOla', 'id': 1, 'user_role': 'admin'}

client = TestClient(app)

@pytest.fixture
def test_todo():
    # 1. Clean the slate completely by recreating tables before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    todo = Todos(
        title="Learn to Code",
        description="Need to Learn Everyday",
        priority=5,
        completed=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    db.refresh(todo) # Ensure the object pulls the fresh IDs from database
    
    yield todo
    
    db.close()


@pytest.fixture
def test_user():
    user = Users(
        username = "codingwithOla",
        email = "oladokunolamide@gmail.com",
        first_name = "Olamide",
        last_name = "Oladokun",
        hashed_password = bcrypt_context.hash("testpassword"), # <-- Add comma here
        role = "admin",                                         # <-- Add comma here
        phone_number = "(234)-234-1111"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
