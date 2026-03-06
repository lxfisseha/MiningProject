from sqlmodel import Session, select
from .exceptions import BusinessLogicError
from src.auth import models as auth_models
from src.auth import exceptions as auth_exceptions
from .models import (
    LicenseHolderProfile,
    EquipmentOwnerProfile,
    ConsultantProfile,
    BuyerProfile,
)
from .schemas import ProfileCreateBase, ProfileUpdateBase
from .exceptions import ProfileInfoMissingError

from uuid import UUID

roles = auth_models.UserRole


def _validate_user_exists(user_id: UUID, session: Session):
    user = session.get(auth_models.User, user_id)
    if not user:
        raise auth_exceptions.UserNotFoundError()

    return user


def _validate_user_has_profile(
    user: auth_models.User, session: Session, ProfileModelClass: type
):
    statement = select(ProfileModelClass).where(ProfileModelClass.user_id == user.id)
    profile = session.exec(statement).first()
    if not profile:
        raise ProfileInfoMissingError()
    _validate_user_role_matches_profile(user, ProfileModelClass)
    return profile


def _validate_user_doesnot_have_profile(
    user_id: UUID, session: Session, ProfileModelClass: type
):
    statement = select(ProfileModelClass).where(ProfileModelClass.user_id == user_id)
    profile = session.exec(statement).first()
    if profile:
        raise ProfileInfoMissingError()
    return profile


def _validate_user_role_matches_profile(user: auth_models.User, ProfileModelClass):
    if user.role == roles.LICENSE_HOLDER and ProfileModelClass == LicenseHolderProfile:
        return
    if user.role == roles.CONSULTANT and ProfileModelClass == ConsultantProfile:
        return
    if user.role == roles.BUYER and ProfileModelClass == BuyerProfile:
        return
    if (
        user.role == EquipmentOwnerProfile
        and ProfileModelClass == EquipmentOwnerProfile
    ):
        return

    raise ProfileInfoMissingError


def create_profile(
    session: Session,
    data: ProfileCreateBase,
    user_id: UUID,
    ProfileModelClass: type,
    commit: bool = True,
):
    user = _validate_user_exists(user_id, session)
    _validate_user_doesnot_have_profile(user_id, session, ProfileModelClass)
    _validate_user_role_matches_profile(user, ProfileModelClass)

    profile = ProfileModelClass.model_validate(data, update={"user_id": user_id})

    session.add(profile)
    if commit:
        session.commit()

    return profile


def update_profile(
    session: Session,
    data: ProfileUpdateBase,
    user_id: UUID,
    ProfileModelClass: type,
    commit: bool = True,
):

    user = _validate_user_exists(user_id, session)
    profile = _validate_user_has_profile(user, session, ProfileModelClass)

    profile.sqlmodel_update(data)

    session.add(profile)

    if commit:
        session.commit()
        session.refresh(profile)

    return profile
