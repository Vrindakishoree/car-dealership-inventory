from app.auth import create_access_token, get_current_user_email
from app.models import User, UserRegister, UserLogin, Vehicle, VehicleCreate
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
import bcrypt

from app.database import create_db_and_tables, get_session, engine
from app.models import User, UserRegister


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Car Dealership Inventory API", lifespan=lifespan)


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