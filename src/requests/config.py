from .enums import RequestType
from src.auth.models import UserRole

ALLOWED_REQUEST_TYPES_TO_ROLES = {
        UserRole.LICENSE_HOLDER: {RequestType.OTHER, RequestType.CONSULTING, RequestType.MINERAL_SELLER, RequestType.LICENSE_SELL},
        UserRole.BUYER: {RequestType.MINERAL_BUYER, RequestType.OTHER},
        UserRole.EQUIPMENT_OWNER: {RequestType.OTHER},
        UserRole.CONSULTANT: {RequestType.OTHER}
}