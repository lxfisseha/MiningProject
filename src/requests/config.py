from .enums import RequestType
from src.auth.models import UserRole

ALLOWED_REQUESTS_TO_ROLES = {
        RequestType.CONSULTING: {UserRole.LICENSE_HOLDER},
        RequestType.MINERAL_SELLER: {UserRole.LICENSE_HOLDER},
        RequestType.LICENSE_SELL: {UserRole.LICENSE_HOLDER},
        RequestType.MINERAL_BUYER: {UserRole.BUYER},
        RequestType.OTHER: set(UserRole)
    }