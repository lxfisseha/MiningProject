from src.auth import models as auth_models
from src.auth import schemas as auth_schemas
from .models import BuyerProfile, LicenseHolderProfile, EquipmentOwnerProfile, ConsultantProfile
from .exceptions import ProfileRoleMissmatch, InvalidRoleError

def _validate_role_profile_consistency(registration_data: auth_schemas.RegistrationRequest):
    if registration_data.role in [auth_models.UserRole.ADMIN, auth_models.UserRole.STAFF]:
        raise InvalidRoleError()
    if registration_data.role == auth_models.UserRole.LICENSE_HOLDER and not registration_data.license_holder_profile:
        raise ProfileRoleMissmatch()
    if registration_data.role == auth_models.UserRole.EQUIPMENT_OWNER and not registration_data.equipment_owner_profile:
        raise ProfileRoleMissmatch()
    if registration_data.role == auth_models.UserRole.CONSULTANT and not registration_data.consultant_profile:
        raise ProfileRoleMissmatch()
    if registration_data.role == auth_models.UserRole.BUYER and not registration_data.buyer_profile:
        raise ProfileRoleMissmatch()


def create_user_profile(registration_data: auth_schemas.RegistrationRequest, session, new_user, commit: bool = False):
    _validate_role_profile_consistency(registration_data)
    if registration_data.role == auth_models.UserRole.LICENSE_HOLDER:
        profile = LicenseHolderProfile(
            user_id=new_user.id,
            **registration_data.license_holder_profile.model_dump()
        )
    elif registration_data.role == auth_models.UserRole.EQUIPMENT_OWNER:
        profile = EquipmentOwnerProfile(
            user_id=new_user.id,
            **registration_data.equipment_owner_profile.model_dump()
        )
    elif registration_data.role == auth_models.UserRole.CONSULTANT:
        profile = ConsultantProfile(
            user_id=new_user.id,
            **registration_data.consultant_profile.model_dump()
        )
    elif registration_data.role == auth_models.UserRole.BUYER:
        profile = BuyerProfile(
            user_id=new_user.id,
            **registration_data.buyer_profile.model_dump()
        )
    else:
        raise InvalidRoleError()

    session.add(profile)
    if commit:
        session.commit()