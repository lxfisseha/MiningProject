import enum

from src.auth import models as auth_models
from src.requests.enums import RequestStatus, RequestType
from pydantic import BaseModel, validator



class RequestsFilters(BaseModel): 
    sorting: str = "lf"
    request_type: RequestType | None = None
    status: RequestStatus | None = None
    user_id: str | None = None
    limit: int = 15
    offset: int = 0

    @validator("request_type", pre=True)    
    def empty_str_to_none(cls, v):
        if v == "" or v == None:
            return None
        elif v not in list(RequestType):
            raise ValueError("Invalid request type")
        return v
    
    @validator("status", pre=True)
    def empty_str_to_none_status(cls, v):
        if v == "" or v == None:
            return None
        elif v not in list(RequestStatus):
            raise ValueError("Invalid request status")
        return v

    @property
    def current_page(self):
        return self.offset // self.limit + 1


class UserSortOptions(str, enum.Enum):
    latest_first = "lf"
    oldest_first = "of"


class UserFilters(BaseModel):
    status: auth_models.UserStatus | None = None
    role: auth_models.UserRole | None = None
    sorting: UserSortOptions = UserSortOptions.latest_first
    search: str = ""
    limit: int = 15
    offset: int = 0

    @validator("role", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v == None:
            return None
        elif v not in list(auth_models.UserRole):
            raise ValueError("Invalid user role")
        return v
    
    @validator("status", pre=True)
    def empty_str_to_none_status(cls, v):
        if v == "" or v == None:
            return None
        elif v not in list(auth_models.UserStatus):
            raise ValueError("Invalid user status")
        return v

    @property
    def current_page(self):
        return self.offset // self.limit + 1