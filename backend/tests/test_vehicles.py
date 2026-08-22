from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.models import User
from sqlmodel import SQLModel, Session, select


def setup_function():
    """Runs before every test: start with a clean, empty database."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def get_auth_token(client):
    """Helper: registers and logs in a regular user, returns their JWT token."""
    client.post(
        "/api/auth/register",
        json={"email": "dealer@example.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "dealer@example.com", "password": "password123"},
    )
    return response.json()["access_token"]


def get_admin_token(client):
    """Helper: registers a user, manually promotes them to admin in the DB, logs in, returns token."""
    client.post(
        "/api/auth/register",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == "admin@example.com")).first()
        user.is_admin = True
        session.add(user)
        session.commit()

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "adminpass123"},
    )
    return response.json()["access_token"]


def add_test_vehicle(client, token):
    """Helper: adds a standard test vehicle, returns its id."""
    response = client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 22000, "quantity": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


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


def test_get_all_vehicles_returns_list():
    """Listing vehicles should return all vehicles that have been added."""
    with TestClient(app) as client:
        token = get_auth_token(client)
        client.post(
            "/api/vehicles",
            json={"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 22000, "quantity": 5},
            headers={"Authorization": f"Bearer {token}"},
        )
        client.post(
            "/api/vehicles",
            json={"make": "Honda", "model": "Civic", "category": "Sedan", "price": 21000, "quantity": 3},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = client.get(
            "/api/vehicles",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        makes = [v["make"] for v in data]
        assert "Toyota" in makes
        assert "Honda" in makes


def test_search_vehicles_by_make():
    """Searching by make should return only matching vehicles."""
    with TestClient(app) as client:
        token = get_auth_token(client)
        client.post(
            "/api/vehicles",
            json={"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 22000, "quantity": 5},
            headers={"Authorization": f"Bearer {token}"},
        )
        client.post(
            "/api/vehicles",
            json={"make": "Honda", "model": "Civic", "category": "Sedan", "price": 21000, "quantity": 3},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = client.get(
            "/api/vehicles/search?make=Toyota",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["make"] == "Toyota"


def test_search_vehicles_by_price_range():
    """Searching by min/max price should return only vehicles in that range."""
    with TestClient(app) as client:
        token = get_auth_token(client)
        client.post(
            "/api/vehicles",
            json={"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 22000, "quantity": 5},
            headers={"Authorization": f"Bearer {token}"},
        )
        client.post(
            "/api/vehicles",
            json={"make": "Porsche", "model": "911", "category": "Sports", "price": 120000, "quantity": 1},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = client.get(
            "/api/vehicles/search?min_price=100000&max_price=150000",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["make"] == "Porsche"


def test_update_vehicle_succeeds():
    """A logged-in user should be able to update a vehicle's details."""
    with TestClient(app) as client:
        token = get_auth_token(client)
        vehicle_id = add_test_vehicle(client, token)

        response = client.put(
            f"/api/vehicles/{vehicle_id}",
            json={"make": "Toyota", "model": "Corolla", "category": "Sedan", "price": 23000, "quantity": 5},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["price"] == 23000


def test_purchase_vehicle_decreases_quantity():
    """Purchasing a vehicle should decrease its quantity by 1."""
    with TestClient(app) as client:
        token = get_auth_token(client)
        vehicle_id = add_test_vehicle(client, token)

        response = client.post(
            f"/api/vehicles/{vehicle_id}/purchase",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["quantity"] == 4


def test_purchase_vehicle_fails_when_out_of_stock():
    """Purchasing a vehicle with 0 quantity should be rejected."""
    with TestClient(app) as client:
        token = get_auth_token(client)
        response = client.post(
            "/api/vehicles",
            json={"make": "Ferrari", "model": "F8", "category": "Sports", "price": 280000, "quantity": 0},
            headers={"Authorization": f"Bearer {token}"},
        )
        vehicle_id = response.json()["id"]

        response = client.post(
            f"/api/vehicles/{vehicle_id}/purchase",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400


def test_delete_vehicle_requires_admin():
    """A regular (non-admin) user should not be able to delete a vehicle."""
    with TestClient(app) as client:
        token = get_auth_token(client)
        vehicle_id = add_test_vehicle(client, token)

        response = client.delete(
            f"/api/vehicles/{vehicle_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


def test_delete_vehicle_succeeds_for_admin():
    """An admin user should be able to delete a vehicle."""
    with TestClient(app) as client:
        regular_token = get_auth_token(client)
        vehicle_id = add_test_vehicle(client, regular_token)

        admin_token = get_admin_token(client)
        response = client.delete(
            f"/api/vehicles/{vehicle_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200


def test_restock_vehicle_succeeds_for_admin():
    """An admin should be able to restock a vehicle, increasing its quantity."""
    with TestClient(app) as client:
        regular_token = get_auth_token(client)
        vehicle_id = add_test_vehicle(client, regular_token)

        admin_token = get_admin_token(client)
        response = client.post(
            f"/api/vehicles/{vehicle_id}/restock?amount=10",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["quantity"] == 15