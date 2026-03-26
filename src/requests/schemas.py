from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, validator
from .exceptions import RequestErrorBase
from src.auth.schemas import UserResponse
from .enums import (
    RequestType,
    RequestStatus,
    ConsultancyType,
    StudyLevel,
    RequestSortOptions,
)

from src.profiles.models import LicenseType


# ===================
# Request Schemas
# ===================
class RequestFilters(BaseModel):
    offset: int = 0
    limit: int = 10
    exclude_cancelled: bool = False
    request_type: RequestType | None | str = None
    sorting: RequestSortOptions = RequestSortOptions.latest_first

    @validator("request_type", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v == None:
            return None
        elif v not in list(RequestType):
            raise RequestErrorBase(422, "Invalid request type")
        return v

    @property
    def current_page(self):
        return self.offset // self.limit + 1


class RequestBase(BaseModel):
    requester_id: UUID
    request_type: RequestType
    status: Optional[RequestStatus] = RequestStatus.NEW
    more_detail: Optional[str] = None


class OtherRequestCreate(BaseModel):
    more_detail: str


class OtherRequestUpdate(BaseModel):
    more_detail: str | None = None


class OtherRequestResponse(RequestBase):
    more_detail: str
    id: UUID


class RequestResponse(RequestBase):
    model_config = ConfigDict(from_attributes=True)

    user: UserResponse | None = None
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
    self_transportation: bool = False
    self_production: bool = False


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
    self_transportation: bool = False
    self_production: bool = False


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


class RequestDetailResponse(RequestResponse):
    consulting_request: ConsultingRequestResponse | None = None
    mineral_buy_request: MineralBuyerRequestResponse | None = None
    mineral_sell_request: MineralSellerRequestResponse | None = None
    license_sell_request: LicenseSellRequestResponse | None = None


class RequestCreate(BaseModel):
    request_type: RequestType
    more_detail: Optional[str] = None

    license_sell_request: LicenseSellRequestCreate | None = None
    mineral_buy_request: MineralBuyerRequestCreate | None = None
    consulting_request: ConsultingRequestCreate | None = None
    mineral_sell_request: MineralSellerRequestCreate | None = None


class RequestUpdate(BaseModel):
    more_detail: str | None = None

    license_sell_request: LicenseSellRequestUpdate | None = None
    mineral_buy_request: MineralBuyerRequestUpdate | None = None
    consulting_request: ConsultingRequestUpdate | None = None
    mineral_sell_request: MineralSellerRequestUpdate | None = None


class UserStatsResponse(BaseModel):
    user_id: UUID
    total_requests: int | None = 0
    pending_requests: int | None = 0
    completed_requests: int | None = 0
