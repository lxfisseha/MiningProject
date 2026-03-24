
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

from . import enums
from src.auth import models as auth_models
from src.profiles import models as profile_models



# =========
# Requests
# =========



class Request(SQLModel, table=True):
    __tablename__ = "requests"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    requester_id: UUID = Field(foreign_key="users.id")

    request_type: enums.RequestType
    status: enums.RequestStatus = enums.RequestStatus.NEW

    more_detail: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    is_deleted: bool = False

    user: auth_models.User = Relationship()

class ConsultingRequest(SQLModel, table=True):
    __tablename__ = "consulting_requests"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    request_id: UUID = Field(foreign_key="requests.id", unique=True)

    consultancy_type: enums.ConsultancyType
    expert_type: str
    drill_machine_required: bool
    study_level: enums.StudyLevel

    location: str
    license_holder_name: str
    license_number: str
    material_type: str

    license_certificate_document_id: Optional[UUID] = None

    request: Request = Relationship()


class MineralSellerRequest(SQLModel, table=True):
    __tablename__ = "mineral_seller_requests"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    request_id: UUID = Field(foreign_key="requests.id", unique=True)

    material_type: str
    location: str
    quantity: str

    license_holder_name: str
    license_number: str

    self_transportation: bool
    self_production: bool

    license_certificate_document_id: Optional[UUID] = None

    request: Request = Relationship()


class LicenseSellRequest(SQLModel, table=True):
    __tablename__ = "license_sell_requests"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    request_id: UUID = Field(foreign_key="requests.id", unique=True)

    license_type: profile_models.LicenseType
    location: str
    material_type: str
    site_area: str

    license_holder_name: str
    license_number: str

    license_certificate_document_id: Optional[UUID] = None
    geological_report_document_id: Optional[UUID] = None

    request: Request = Relationship()


class MineralBuyerRequest(SQLModel, table=True):
    __tablename__ = "mineral_buyer_requests"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    request_id: UUID = Field(foreign_key="requests.id", unique=True)

    material_type: str
    location: str
    quantity: str

    buyer_name: str
    contact_information: str

    self_transportation: bool
    self_production: bool
    collaboration_interest: str

    request: Request = Relationship()
