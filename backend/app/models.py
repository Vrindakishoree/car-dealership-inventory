from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_admin: bool = Field(default=False)

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str  


from typing import Optional
from sqlmodel import SQLModel, Field


class Vehicle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    make: str
    model: str
    category: str
    price: float
    quantity: int = Field(default=0)


class VehicleCreate(BaseModel):
    make: str
    model: str
    category: str
    price: float
    quantity: int