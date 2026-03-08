from datetime import timedelta
from sqlmodel import UUID, Session, select
from fastapi import Depends, Form, Request
from typing import Annotated

from .utils import hash_password, verify_password, create_access_token
from .models import User, UserAuth, UserRole, UserStatus
from .schemas import RegistrationRequest, LoginRequest, TokenResponse

from .exceptions import LoginError, UserNotFoundError, EmailExistsError, FailedToCreateAuthRecord, \
    ProfileCreationFailedError
from src.profiles import services as profile_services


def login_service(login_data: LoginRequest, session: Session) -> TokenResponse:
    statement = select(User).where(User.email == login_data.email)
    user = session.exec(statement).first()

    if not user:
        raise LoginError()
    if user.status != UserStatus.APPROVED:
        raise LoginError()
    if not user.user_auth:
        raise LoginError()
    if not verify_password(login_data.password, user.user_auth.hashed_password):
        raise LoginError()

    token = create_access_token({"sub": str(user.id), "role": user.role})

    return TokenResponse(access_token=token)


def registration_service(registration_data: RegistrationRequest, session: Session):
    statement = select(User).where(User.email == registration_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise EmailExistsError()
    # Create new user
    new_user = User(
        full_name=registration_data.full_name,
        email=registration_data.email,
        phone=registration_data.phone,
        role=registration_data.role,
    )
    session.add(new_user)
    session.flush()

    _create_user_auth_record(registration_data.password, new_user.id, session)
    profile_services.create_user_profile(registration_data, session, new_user)

    session.commit()
    session.refresh(new_user)
    return new_user

def _create_user_auth_record(password: str, user_id: UUID, session: Session):
    try:
        hashed_password = hash_password(password)
        user_auth = UserAuth(user_id=user_id, hashed_password=hashed_password)
        session.add(user_auth)
    except:
        raise FailedToCreateAuthRecord()