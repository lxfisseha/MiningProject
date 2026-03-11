from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict
from .enums import RequestType, RequestStatus, ConsultancyType, StudyLevel

from src.profiles.models import LicenseType


# ===================
# Request Schemas
# ===================

class RequestBase(BaseModel):
    requester_id: UUID
    request_type: RequestType
    status: Optional[RequestStatus] = RequestStatus.NEW


class OtherRequestCreate(BaseModel):
    more_detail: str


class OtherRequestUpdate(BaseModel):
    more_detail: str | None = None


class OtherRequestResponse(RequestBase):
    more_detail: str
    id: UUID


class RequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None


class RequestResponse(RequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# =========================
# ConsultingRequest Schemas
# =========================

class ConsultingRequestBase(BaseModel):
    consultancy_type: ConsultancyType
    expert_type: str
    drill_machine_required: bool = False
    study_level: StudyLevel
    location: str
    license_holder_name: str
    license_number: str
    material_type: str
    license_certificate_document_id: Optional[UUID] = None


class ConsultingRequestCreate(ConsultingRequestBase):
    pass


class ConsultingRequestUpdate(BaseModel):
    consultancy_type: Optional[ConsultancyType] = None
    expert_type: Optional[str] = None
    drill_machine_required: Optional[bool] = None
    study_level: Optional[StudyLevel] = None
    location: Optional[str] = None
    license_holder_name: Optional[str] = None
    license_number: Optional[str] = None
    material_type: Optional[str] = None
    license_certificate_document_id: Optional[UUID] = None


class ConsultingRequestResponse(ConsultingRequestBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    request_id: UUID
    request: Optional[RequestResponse] = None


# =========================
# MineralSellerRequest Schemas
# =========================

class MineralSellerRequestBase(BaseModel):
    material_type: str
    location: str
    quantity: str
    license_holder_name: str
    license_number: str
    self_transportation: bool
    self_production: bool
    license_certificate_document_id: Optional[UUID] = None


class MineralSellerRequestCreate(MineralSellerRequestBase):
    pass


class MineralSellerRequestUpdate(BaseModel):
    material_type: Optional[str] = None
    license_holder_name: Optional[str] = None
    license_number: Optional[str] = None
    self_transportation: Optional[bool] = None
    self_production: Optional[bool] = None
    license_certificate_document_id: Optional[UUID] = None
    location: Optional[str] = None
    quantity: Optional[str] = None


class MineralSellerRequestResponse(MineralSellerRequestBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    request: Optional[RequestResponse] = None


# =========================
# LicenseSellRequest Schemas
# =========================

class LicenseSellRequestBase(BaseModel):
    license_type: LicenseType
    location: str
    material_type: str
    site_area: str
    license_holder_name: str
    license_number: str
    license_certificate_document_id: Optional[UUID] = None
    geological_report_document_id: Optional[UUID] = None


class LicenseSellRequestCreate(LicenseSellRequestBase):
    pass


class LicenseSellRequestUpdate(BaseModel):
    license_type: Optional[LicenseType] = None
    material_type: Optional[str] = None
    license_holder_name: Optional[str] = None
    license_number: Optional[str] = None
    license_certificate_document_id: Optional[UUID] = None
    geological_report_document_id: Optional[UUID] = None
    location: Optional[str] = None
    site_area: Optional[str] = None


class LicenseSellRequestResponse(LicenseSellRequestBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    request: Optional[RequestResponse] = None


# =========================
# MineralBuyerRequest Schemas
# =========================

class MineralBuyerRequestBase(BaseModel):
    material_type: str
    location: str
    quantity: str
    buyer_name: str
    contact_information: str
    self_transportation: bool
    self_production: bool
    collaboration_interest: str


class MineralBuyerRequestCreate(MineralBuyerRequestBase):
    pass


class MineralBuyerRequestUpdate(BaseModel):
    location: Optional[str] = None
    quantity: Optional[str] = None
    material_type: Optional[str] = None
    buyer_name: Optional[str] = None
    contact_information: Optional[str] = None
    self_transportation: Optional[bool] = None
    self_production: Optional[bool] = None
    collaboration_interest: Optional[str] = None


class MineralBuyerRequestResponse(MineralBuyerRequestBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    request: Optional[RequestResponse] = None


