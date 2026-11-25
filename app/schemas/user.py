from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str | None = None

class Userlogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    phone: str | None = Field(default=None, min_length=10, max_length=15)

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)