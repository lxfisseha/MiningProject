from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .models import UserRole, UserStatus


class ChangeMyPasswordRequest(BaseModel):
    current_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id: Optional[UUID] = None
    role: Optional[UserRole] = None


class UserBase(BaseModel):
    full_name: str = Field(min_length=2)
    email: EmailStr
    phone: str
    role: UserRole
    preferred_language: str = "EN"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterUserRequest(UserBase):
    password: str = Field(min_length=8)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: UserStatus
    created_at: datetime


class MeResponse(UserResponse):
    pass


class RegistrationStatusResponse(BaseModel):
    status: UserStatus
    message: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None
