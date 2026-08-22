import os
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from sqlmodel import SQLModel


def setup_function():
    """Runs before every test: start with a clean, empty database."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_register_new_user_succeeds():
    """A new user should be able to register with an email and password."""
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "securepassword123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "password" not in data