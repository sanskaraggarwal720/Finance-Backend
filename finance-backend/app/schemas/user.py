from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import Role


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: Role = Role.viewer


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    is_active: bool

    class Config:
        from_attributes = True
