from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from .models import LicenseType
from src.auth import models as auth_models
from src.auth import schemas as auth_schemas
from ..auth.schemas import UserResponse


class BaseProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    office_address: Optional[str] = None


class LicenseHolderProfileUpdate(BaseProfileUpdate):
    site_address: Optional[str] = None
    license_type: Optional[LicenseType] = None
    material_type: Optional[str] = None
    license_number: Optional[str] = None

    license_certificate_document_id: Optional[UUID] = None
    geological_report_document_id: Optional[UUID] = None
    national_id_document_id: Optional[UUID] = None

class EquipmentOwnerProfileUpdate(BaseProfileUpdate):
    equipment_types_owned: Optional[str] = None

    trade_license_document_id: Optional[UUID] = None
    national_id_document_id: Optional[UUID] = None


class ConsultantProfileUpdate(BaseProfileUpdate):
    expertise_areas: Optional[str] = None
    years_of_experience: Optional[str] = None

    national_id_document_id: Optional[UUID] = None
    professional_license_document_id: Optional[UUID] = None
    supporting_document_id: Optional[UUID] = None

class BuyerProfileUpdate(BaseProfileUpdate):
    industry_type: Optional[str] = None
    plant_location: Optional[str] = None

    supporting_document_id: Optional[UUID] = None

class UserAndProfileUpdate(BaseModel):
    user: Optional[auth_schemas.UserUpdate] = None

    license_holder_profile: Optional[LicenseHolderProfileUpdate] = None
    equipment_owner_profile: Optional[EquipmentOwnerProfileUpdate] = None
    consultant_profile: Optional[ConsultantProfileUpdate] = None
    buyer_profile: Optional[BuyerProfileUpdate] = None

class ProfileCreateBase(BaseModel):
    company_name: str | None = None
    office_address: str | None = None


class LicenseHolderCreate(ProfileCreateBase):
    site_address: str
    license_type: LicenseType
    material_type: str
    license_number: str


class EquipmentOwnerCreate(ProfileCreateBase):
    equipment_types_owned: str


class ConsultantCreate(ProfileCreateBase):
    expertise_areas: str
    years_of_experience: str


class BuyerCreate(ProfileCreateBase):
    industry_type: str
    plant_location: str


class ProfileBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    approval_fee_paid: bool
    company_name: Optional[str] = None
    office_address: Optional[str] = None

    created_at: datetime
    updated_at: datetime


class LicenseHolderProfileResponse(ProfileBaseResponse):
    site_address: str
    license_type: LicenseType
    material_type: str
    license_number: str

    license_certificate_document_id: Optional[UUID] = None
    geological_report_document_id: Optional[UUID] = None
    national_id_document_id: Optional[UUID] = None

    user: auth_models.User


class EquipmentOwnerProfileResponse(ProfileBaseResponse):
    equipment_types_owned: str

    trade_license_document_id: Optional[UUID] = None
    national_id_document_id: Optional[UUID] = None

    user: auth_models.User


class ConsultantProfileResponse(ProfileBaseResponse):
    expertise_areas: str
    years_of_experience: str

    national_id_document_id: Optional[UUID] = None
    professional_license_document_id: Optional[UUID] = None
    supporting_document_id: Optional[UUID] = None

    user: auth_models.User


class BuyerProfileResponse(ProfileBaseResponse):
    industry_type: str
    plant_location: str

    supporting_document_id: Optional[UUID] = None

    user: auth_models.User


class UserAndProfileResponse(UserResponse):
    license_holder_profile: Optional[LicenseHolderProfileResponse] = None
    equipment_owner_profile: Optional[EquipmentOwnerProfileResponse] = None
    consultant_profile: Optional[ConsultantProfileResponse] = None
    buyer_profile: Optional[BuyerProfileResponse] = None



class ProfileRegistrationRequest(BaseModel):
    license_holder_profile: Optional[LicenseHolderCreate] = None
    equipment_owner_profile: Optional[EquipmentOwnerCreate] = None
    consultant_profile: Optional[ConsultantCreate] = None
    buyer_profile: Optional[BuyerCreate] = None

class ProfileUpdateRequest(BaseModel):
    license_holder_profile: Optional[LicenseHolderProfileUpdate] = None
    equipment_owner_profile: Optional[EquipmentOwnerProfileUpdate] = None
    consultant_profile: Optional[ConsultantProfileUpdate] = None
    buyer_profile: Optional[BuyerProfileUpdate] = None