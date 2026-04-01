from datetime import timedelta
from sqlmodel import UUID, Session, select
from fastapi import Depends, Form, Request
from typing import Annotated

from .utils import hash_password, verify_password, create_access_token
from .models import User, UserAuth, UserRole, UserStatus
from .schemas import (
    LoginRequest,
    TokenResponse,
    RegisterUserRequest,
    ChangeMyPasswordRequest,
    UserUpdate,
)

from .exceptions import (
    LoginError,
    UserNotFoundError,
    EmailExistsError,
    FailedToCreateAuthRecord,
    UnApprovedUserErrorLogin,
    AuthenticationErrorBase,
)
from .exceptions import WrongPasswordError, NotAllowedError
from ..profiles.exceptions import NotAllowed


def get_user_by_id(user_id: UUID, session: Session):
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError()
    return user


def login_service(login_data: LoginRequest, session: Session) -> User:
    statement = select(User).where(User.email == login_data.email)
    user = session.exec(statement).first()

    if not user:
        raise LoginError()
    if not user.user_auth:
        raise LoginError()
    if not verify_password(login_data.password, user.user_auth.hashed_password):
        raise LoginError()
    if user.status != UserStatus.APPROVED:
        raise UnApprovedUserErrorLogin()

    return user


def registration_service(registration_data: RegisterUserRequest, session: Session):
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

    session.commit()
    session.refresh(new_user)
    return new_user


def _create_user_auth_record(password: str, user_id: UUID, session: Session):
    hashed_password = hash_password(password)
    user_auth = UserAuth(user_id=user_id, hashed_password=hashed_password)
    session.add(user_auth)


def update_user(actor: User, user_id: UUID, data: UserUpdate, session: Session):
    user = session.get(User, user_id)

    if not user:
        raise UserNotFoundError()
    if not actor:
        raise NotAllowed()

    if user.id != actor.id and (not actor.is_staff_or_admin):
        raise NotAllowed()

    if data.email:
        existing_user = session.exec(
            select(User).where(User.email == data.email)
        ).first()
        if existing_user and existing_user.id != user_id:
            raise EmailExistsError()

    updated_user = user.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(updated_user)
    session.commit()
    session.refresh(updated_user)

    return updated_user


def change_my_password(
    session: Session, actor: User, user_id: UUID, data: ChangeMyPasswordRequest
):
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError
    if actor.id != user.id:
        raise NotAllowedError()

    if not verify_password(data.current_password, user.user_auth.hashed_password):
        raise WrongPasswordError()

    user.user_auth.hashed_password = hash_password(data.new_password)
    session.add(user.user_auth)
    session.commit()
    return 1

def change_user_status(
    actor: User,
    session: Session,
    user_id: UUID,
    status: UserStatus,
):
    if not actor.is_staff_or_admin:
        raise NotAllowedError()

    user = get_user_by_id(user_id, session)
    user.status = status
    session.add(user)
    session.commit()
    session.refresh(user)
    return user