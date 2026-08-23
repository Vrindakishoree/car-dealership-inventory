# Car Dealership Inventory System

A full-stack inventory management system for a car dealership, built as a TDD kata. Users can register, log in, browse and search vehicles, and purchase them. Admin users can additionally add, update, delete, and restock vehicles.

## Tech Stack

**Backend:** Python, FastAPI, SQLModel (SQLite), JWT authentication (python-jose), bcrypt for password hashing, pytest for testing

**Frontend:** React (Vite), Tailwind CSS, React Router

## Features

- User registration and login with JWT-based authentication
- Browse all vehicles in inventory
- Search/filter vehicles by make, model, category, and price range
- Purchase a vehicle (disabled automatically when out of stock)
- Admin-only: add, update, delete, and restock vehicles

## Project Structure


## Setup Instructions

### Backend

1. Navigate to the backend folder and create a virtual environment:
cd backend
python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # macOS/Linux

2. Install dependencies:
pip install -r requirements.txt


3. Create a `.env` file in the `backend` folder with:
JWT_SECRET_KEY=your-secret-key-here


4. Run the server:
uvicorn app.main:app --reload --port 8000


   The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

### Frontend

1. In a separate terminal, navigate to the frontend folder:
cd frontend
npm install

2. Run the dev server:

npm run dev


   The app will be available at `http://localhost:5173`.

**Note:** both the backend and frontend servers must be running simultaneously for the app to work.

### Making a user an admin

New users register as regular users by default. To test admin features, manually promote a user in the database (a temporary one-off script, since a full admin-promotion flow was outside the assignment's scope):

```python
from app.database import engine
from app.models import User
from sqlmodel import Session, select

with Session(engine) as session:
    user = session.exec(select(User).where(User.email == "your-email@example.com")).first()
    user.is_admin = True
    session.add(user)
    session.commit()
```

## Running Tests

cd backend
pytest -v

### Test Report

============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
collected 14 items

tests/test_auth.py::test_register_new_user_succeeds PASSED [ 7%]
tests/test_auth.py::test_login_with_correct_credentials_returns_token PASSED [ 14%]
tests/test_auth.py::test_login_with_wrong_password_fails PASSED [ 21%]
tests/test_vehicles.py::test_add_vehicle_requires_authentication PASSED [ 28%]
tests/test_vehicles.py::test_add_vehicle_with_valid_token_succeeds PASSED [ 35%]
tests/test_vehicles.py::test_get_all_vehicles_returns_list PASSED [ 42%]
tests/test_vehicles.py::test_search_vehicles_by_make PASSED [ 50%]
tests/test_vehicles.py::test_search_vehicles_by_price_range PASSED [ 57%]
tests/test_vehicles.py::test_update_vehicle_succeeds PASSED [ 64%]
tests/test_vehicles.py::test_purchase_vehicle_decreases_quantity PASSED [ 71%]
tests/test_vehicles.py::test_purchase_vehicle_fails_when_out_of_stock PASSED [ 78%]
tests/test_vehicles.py::test_delete_vehicle_requires_admin PASSED [ 85%]
tests/test_vehicles.py::test_delete_vehicle_succeeds_for_admin PASSED [ 92%]
tests/test_vehicles.py::test_restock_vehicle_succeeds_for_admin PASSED [100%]

======================= 14 passed, 1 warning in 10.43s ========================



## My AI Usage

**AI tools used:** Claude (Anthropic), via claude.ai

**How I used it:**

I used Claude as a pair-programming partner throughout this project, following a consistent TDD workflow: for each feature, we discussed the requirement, Claude helped me write a failing test first, then we implemented the minimum code to make it pass, and refactored when needed.

Specifically, Claude helped me:
- Scaffold the FastAPI backend structure (models, database setup, routing)
- Design the JWT authentication flow and the dependency-injection pattern FastAPI uses for protecting routes
- Debug several real errors as they came up, including a FastAPI validation issue (query params vs. request body), a database table not being created before tests ran, a passlib/bcrypt version incompatibility, and a CORS misconfiguration blocking the frontend from reaching the backend
- Scaffold the React frontend (Vite + Tailwind + React Router setup)
- Design the AuthContext pattern for sharing login state across the app
- Build individual components (VehicleCard, AddVehicleForm, SearchBar) and wire them into the Dashboard

**Reflection:**

Using AI this way meant I always understood *why* a piece of code worked, not just that it worked — every fix came with an explanation, and I was the one running commands, reading errors, and confirming behavior at each step. It significantly sped up scaffolding (auth, routing, boilerplate) and was especially useful for debugging, since some of the errors I hit (deprecated FastAPI patterns, dependency version mismatches) would have taken much longer to research alone. At the same time, I made sure to actually test and verify each change myself rather than blindly trusting generated code — several early attempts had bugs (like incorrect status codes or shared test state) that we caught and fixed together through the actual test suite, not by assumption.

Raw chat logs are available in [`PROMPTS.md`](./PROMPTS.md).