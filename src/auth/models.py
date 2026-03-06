from sqlmodel import Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
import enum
from typing import TYPE_CHECKING
from src.models import BaseSQLModel


class UserRole(str, enum.Enum):
    LICENSE_HOLDER = "license Holder"
    EQUIPMENT_OWNER = "equpment Owner"
    CONSULTANT = "consultant"
    BUYER = "buyer"
    STAFF = "staff"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class User(BaseSQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    full_name: str
    email: str = Field(unique=True, index=True)
    phone: str

    role: UserRole
    status: UserStatus = UserStatus.PENDING
    preferred_language: str = "EN"

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user_auth: Optional["UserAuth"] = Relationship()


class UserAuth(BaseSQLModel, table=True):
    __tablename__ = "user_auth"
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    hashed_password: str
