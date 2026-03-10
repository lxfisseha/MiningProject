from sqlmodel import select, Session

from src.auth import models as auth_models
from .models import BuyerProfile, LicenseHolderProfile, EquipmentOwnerProfile, ConsultantProfile
from .exceptions import ProfileInfoMissingError, InvalidRoleError, UserAlreadyHasProfileError
from .schemas import ProfileRegistrationRequest, LicenseHolderCreate, EquipmentOwnerCreate, BuyerCreate, \
    ConsultantCreate
from uuid import UUID

from ..auth.services import get_user_by_id

def create_user_profile(registration_data: ProfileRegistrationRequest, session: Session, user_id: UUID):
    user = get_user_by_id(user_id, session)
    _validate_role_profile_consistency(registration_data, user.role)
    if user.role == auth_models.UserRole.LICENSE_HOLDER:
        profile = create_license_holder_profile(registration_data.license_holder_profile, session, user.id)
    elif user.role == auth_models.UserRole.EQUIPMENT_OWNER:
        profile = create_equipment_owner_profile(registration_data.equipment_owner_profile, session, user.id)
    elif user.role == auth_models.UserRole.CONSULTANT:
        profile = create_consultant_profile(registration_data.consultant_profile, session, user.id)
    elif user.role == auth_models.UserRole.BUYER:
        profile = create_buyer_profile(registration_data.buyer_profile, session, user.id)
    else:
        raise InvalidRoleError()
    return profile

def create_buyer_profile(data: BuyerCreate, session, user_id):
    existing_profile = session.exec(select(BuyerProfile).where(BuyerProfile.user_id == user_id)).first()
    if existing_profile:
        raise UserAlreadyHasProfileError()
    profile = BuyerProfile.model_validate(data, update={"user_id": user_id})
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def create_consultant_profile(data: ConsultantCreate, session, user_id):
    existing_profile = session.exec(select(ConsultantProfile).where(ConsultantProfile.user_id == user_id)).first()
    if existing_profile:
        raise UserAlreadyHasProfileError()
    profile = ConsultantProfile.model_validate(data, update={"user_id": user_id})
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def create_equipment_owner_profile(data: EquipmentOwnerCreate, session, user_id):
    existing_profile = session.exec(select(EquipmentOwnerProfile).where(EquipmentOwnerProfile.user_id == user_id)).first()
    if existing_profile:
        raise UserAlreadyHasProfileError()
    profile = EquipmentOwnerProfile.model_validate(data, update={"user_id": user_id})
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def create_license_holder_profile(data: LicenseHolderCreate, session, user_id):
    existing_profile = session.exec(select(LicenseHolderProfile).where(LicenseHolderProfile.user_id == user_id)).first()
    if existing_profile:
        raise UserAlreadyHasProfileError()

    profile = LicenseHolderProfile.model_validate(data, update={"user_id": user_id})
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def _validate_role_profile_consistency(registration_data: ProfileRegistrationRequest, role: auth_models.UserRole):
    if role in [auth_models.UserRole.ADMIN, auth_models.UserRole.STAFF]:
        raise InvalidRoleError()
    if role == auth_models.UserRole.LICENSE_HOLDER and not registration_data.license_holder_profile:
        raise ProfileInfoMissingError()
    if role == auth_models.UserRole.EQUIPMENT_OWNER and not registration_data.equipment_owner_profile:
        raise ProfileInfoMissingError()
    if role == auth_models.UserRole.CONSULTANT and not registration_data.consultant_profile:
        raise ProfileInfoMissingError()
    if role == auth_models.UserRole.BUYER and not registration_data.buyer_profile:
        raise ProfileInfoMissingError()
