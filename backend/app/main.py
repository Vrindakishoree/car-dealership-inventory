from app.auth import create_access_token, get_current_user_email, get_current_admin_user
from app.models import User, UserRegister, UserLogin, Vehicle, VehicleCreate
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
import bcrypt
from typing import List
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables, get_session, engine
from app.models import User, UserRegister


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Car Dealership Inventory API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/auth/register", status_code=201)
def register(user_data: UserRegister):
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = bcrypt.hashpw(user_data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = User(email=user_data.email, hashed_password=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)

        return {"id": user.id, "email": user.email}

@app.post("/api/auth/login")
def login(credentials: UserLogin):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == credentials.email)).first()

        if not user or not bcrypt.checkpw(
            credentials.password.encode("utf-8"), user.hashed_password.encode("utf-8")
        ):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token(data={"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}

@app.post("/api/vehicles", status_code=201)
def add_vehicle(
    vehicle_data: VehicleCreate,
    current_user_email: str = Depends(get_current_user_email),
):
    with Session(engine) as session:
        vehicle = Vehicle(**vehicle_data.model_dump())
        session.add(vehicle)
        session.commit()
        session.refresh(vehicle)
        return vehicle



@app.get("/api/vehicles", response_model=List[Vehicle])
def get_vehicles(current_user_email: str = Depends(get_current_user_email)):
    with Session(engine) as session:
        vehicles = session.exec(select(Vehicle)).all()
        return vehicles

    


@app.get("/api/vehicles/search", response_model=List[Vehicle])
def search_vehicles(
    make: Optional[str] = None,
    model: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    current_user_email: str = Depends(get_current_user_email),
):
    with Session(engine) as session:
        query = select(Vehicle)

        if make:
            query = query.where(Vehicle.make == make)
        if model:
            query = query.where(Vehicle.model == model)
        if category:
            query = query.where(Vehicle.category == category)
        if min_price is not None:
            query = query.where(Vehicle.price >= min_price)
        if max_price is not None:
            query = query.where(Vehicle.price <= max_price)

        vehicles = session.exec(query).all()
        return vehicles

@app.put("/api/vehicles/{vehicle_id}", response_model=Vehicle)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleCreate,
    current_user_email: str = Depends(get_current_user_email),
):
    with Session(engine) as session:
        vehicle = session.get(Vehicle, vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        vehicle.make = vehicle_data.make
        vehicle.model = vehicle_data.model
        vehicle.category = vehicle_data.category
        vehicle.price = vehicle_data.price
        vehicle.quantity = vehicle_data.quantity

        session.add(vehicle)
        session.commit()
        session.refresh(vehicle)
        return vehicle


@app.post("/api/vehicles/{vehicle_id}/purchase", response_model=Vehicle)
def purchase_vehicle(
    vehicle_id: int,
    current_user_email: str = Depends(get_current_user_email),
):
    with Session(engine) as session:
        vehicle = session.get(Vehicle, vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        if vehicle.quantity <= 0:
            raise HTTPException(status_code=400, detail="Vehicle is out of stock")

        vehicle.quantity -= 1
        session.add(vehicle)
        session.commit()
        session.refresh(vehicle)
        return vehicle

@app.delete("/api/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    current_user_email: str = Depends(get_current_admin_user),
):
    with Session(engine) as session:
        vehicle = session.get(Vehicle, vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        session.delete(vehicle)
        session.commit()
        return {"message": "Vehicle deleted successfully"}


@app.post("/api/vehicles/{vehicle_id}/restock", response_model=Vehicle)
def restock_vehicle(
    vehicle_id: int,
    amount: int,
    current_user_email: str = Depends(get_current_admin_user),
):
    with Session(engine) as session:
        vehicle = session.get(Vehicle, vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        vehicle.quantity += amount
        session.add(vehicle)
        session.commit()
        session.refresh(vehicle)
        return vehicle

@app.get("/api/auth/me")
def get_me(current_user_email: str = Depends(get_current_user_email)):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == current_user_email)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"email": user.email, "is_admin": user.is_admin}