from sqlmodel import Field, Relationship
from src.models import BaseSQLModel
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from src.auth import models as auth_models
import enum


class LicenseType(str, enum.Enum):
    EXPLORATION = "EXPLORATION"
    MINING = "MINING"


class UserProfile(BaseSQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)

    approval_fee_paid: bool = False
    company_name: str | None = None
    office_address: str | None = None


class LicenseHolderProfile(UserProfile, table=True):
    __tablename__ = "license_holder_profiles"

    site_address: str
    license_type: LicenseType
    material_type: str
    license_number: str

    license_certificate_document_id: Optional[UUID] = None
    geological_report_document_id: Optional[UUID] = None
    national_id_document_id: Optional[UUID] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: auth_models.User = Relationship()


class EquipmentOwnerProfile(UserProfile, table=True):
    __tablename__ = "equipment_owner_profiles"

    equipment_types_owned: str

    trade_license_document_id: Optional[UUID] = None
    national_id_document_id: Optional[UUID] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: auth_models.User = Relationship()


class ConsultantProfile(UserProfile, table=True):
    __tablename__ = "consultant_profiles"

    expertise_areas: str
    years_of_experience: str

    national_id_document_id: Optional[UUID] = None
    professional_license_document_id: Optional[UUID] = None
    supporting_document_id: Optional[UUID] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: auth_models.User = Relationship()


class BuyerProfile(UserProfile, table=True):
    __tablename__ = "buyer_profiles"

    industry_type: str
    plant_location: str

    supporting_document_id: Optional[UUID] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: auth_models.User = Relationship()
