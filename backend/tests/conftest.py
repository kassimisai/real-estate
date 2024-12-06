import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, patch
from app.main import app
from app.core.database import get_db
from app.models.base import Base

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def mock_supabase():
    with patch("app.core.auth.supabase") as mock:
        mock.auth = MagicMock()
        mock.table = MagicMock()
        yield mock

@pytest.fixture(scope="function")
def client(db, mock_supabase):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_user(client):
    user_data = {
        "email": "test@example.com",
        "password": "test_password",
        "full_name": "Test User"
    }
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 201
    return user_data
