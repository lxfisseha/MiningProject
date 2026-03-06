from datetime import datetime, timezone
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


class RegistrationRequest(UserBase):
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
