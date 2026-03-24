from sqlmodel import select, Session, SQLModel

from src.auth import models as auth_models
from .models import BuyerProfile, LicenseHolderProfile, EquipmentOwnerProfile, ConsultantProfile, UserProfile
from .exceptions import ProfileInfoMissingError, InvalidRoleError, UserAlreadyHasProfileError, NotAllowed, \
    IncompleteRegistrationProfileNotFoundError
from .schemas import ProfileRegistrationRequest, LicenseHolderCreate, EquipmentOwnerCreate, BuyerCreate, \
    ConsultantCreate, ProfileUpdateRequest, UserAndProfileResponse, LicenseHolderProfileResponse, BuyerProfileResponse, \
    ConsultantProfileResponse, EquipmentOwnerProfileResponse
from uuid import UUID

from src.auth.exceptions import UserNotFoundError
from src.auth.models import User, UserRole
from src.auth.services import get_user_by_id

role_to_profile_model_map = {
    UserRole.LICENSE_HOLDER: LicenseHolderProfile,
    UserRole.BUYER: BuyerProfile,
    UserRole.CONSULTANT: ConsultantProfile,
    UserRole.EQUIPMENT_OWNER: EquipmentOwnerProfile
}

role_to_profile_response_model_map = {
    UserRole.LICENSE_HOLDER: LicenseHolderProfileResponse,
    UserRole.BUYER: BuyerProfileResponse,
    UserRole.CONSULTANT: ConsultantProfileResponse,
    UserRole.EQUIPMENT_OWNER: EquipmentOwnerProfileResponse
}

role_to_profile_model_data_attribute_name_map = {
    UserRole.LICENSE_HOLDER: "license_holder_profile",
    UserRole.BUYER: "buyer_profile",
    UserRole.CONSULTANT: "consultant_profile",
    UserRole.EQUIPMENT_OWNER: "equipment_owner_profile"
}



def get_profile_model(role:UserRole) -> type:
    model = role_to_profile_model_map.get(role, None)
    if not model: raise InvalidRoleError()
    return model

def get_profile_response_model(role: UserRole) -> type:
    model = role_to_profile_response_model_map.get(role, None)
    if not model: raise InvalidRoleError()
    return model

def get_profile_data_attribute_name(role: UserRole) -> str:
    attr = role_to_profile_model_data_attribute_name_map.get(role, None)
    if not attr:
        raise InvalidRoleError()
    return attr

def create_user_profile(registration_data: ProfileRegistrationRequest, session: Session, user_id: UUID):
    user = get_user_by_id(user_id, session)

    model = get_profile_model(user.role)

    existing_profile = session.exec(select(model).where(model.user_id == user_id)).first()
    if existing_profile:
        raise UserAlreadyHasProfileError()

    attr = get_profile_data_attribute_name(user.role)
    profile_data = getattr(registration_data, attr, None)
    if not profile_data:
        raise ProfileInfoMissingError()

    profile = model.model_validate(profile_data, update={"user_id": user_id})

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def update_profile(actor: User, user_id: UUID, data: ProfileUpdateRequest, session: Session):
    user = get_user_by_id(user_id, session)
    if not user:
        raise UserNotFoundError()
    if not actor:
        raise NotAllowed()

    if user.id != actor.id and actor.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise NotAllowed()

    profile = get_profile_by_user(user, session)
    data_attribute_name = get_profile_data_attribute_name(user.role)

    profile_update_data = getattr(data, data_attribute_name, None)
    updated_profile = profile.sqlmodel_update(profile_update_data.model_dump(exclude_unset=True))

    session.add(updated_profile)
    session.commit()
    session.refresh(updated_profile)
    return updated_profile

def get_profile_by_user(user: auth_models.User, session: Session) -> UserProfile:
    model = get_profile_model(user.role)

    profile: UserProfile = session.exec(
        select(model).where(model.user_id == user.id)
    ).first()

    if not profile:
        raise IncompleteRegistrationProfileNotFoundError(user_id=user.id)
    return profile


def get_user_with_profile(user: User, session: Session) -> UserAndProfileResponse:
    response = UserAndProfileResponse.model_validate(user)
    profile = get_profile_by_user(user, session).model_dump()

    attr = get_profile_data_attribute_name(user.role)
    profile_response = get_profile_response_model(user.role).model_validate(profile)

    setattr(response, attr, profile_response)
    return response
