from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None


class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str
    is_active: bool
    full_name: str | None
    created_at: datetime
