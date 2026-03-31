import enum

from src.auth import models as auth_models

from pydantic import BaseModel


class UserSortOptions(str, enum.Enum):
    latest_first = "lf"
    oldest_first = "of"


class UserFilters(BaseModel):
    status: auth_models.UserStatus | None = None
    role: auth_models.UserRole | None = None
    sorting: UserSortOptions = UserSortOptions.latest_first
    search: str = ""
