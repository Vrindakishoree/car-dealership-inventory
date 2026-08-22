from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from sqlmodel import SQLModel


def setup_function():
    """Runs before every test: start with a clean, empty database."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def get_auth_token(client):
    """Helper: registers and logs in a user, returns their JWT token."""
    client.post(
        "/api/auth/register",
        json={"email": "dealer@example.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "dealer@example.com", "password": "password123"},
    )
    return response.json()["access_token"]


def test_add_vehicle_requires_authentication():
    """Adding a vehicle without a token should be rejected."""
    with TestClient(app) as client:
        response = client.post(
            "/api/vehicles",
            json={"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 22000, "quantity": 5},
        )
        assert response.status_code == 401


def test_add_vehicle_with_valid_token_succeeds():
    """A logged-in user should be able to add a new vehicle."""
    with TestClient(app) as client:
        token = get_auth_token(client)
        response = client.post(
            "/api/vehicles",
            json={"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 22000, "quantity": 5},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["make"] == "Toyota"
        assert data["quantity"] == 5
        assert "id" in data