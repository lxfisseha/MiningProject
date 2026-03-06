from sqlmodel import UUID, Session, select
from fastapi.security import OAuth2PasswordRequestForm
from .exceptions import CredentialsError, EmailExistsError, UserNotFoundError
from src.exceptions import PermisionError
from .utils import hash_password, verify_password, create_access_token
from .models import User, UserAuth, UserRole, UserStatus
from .schemas import (
    RegistrationRequest,
    TokenResponse,
    ChangeMyPasswordRequest,
)


def login_service(
    login_data: OAuth2PasswordRequestForm, session: Session
) -> TokenResponse:
    statement = select(User).where(User.email == login_data.username)
    user = session.exec(statement).first()

    if not user:
        raise CredentialsError()
    if user.status != UserStatus.APPROVED:
        raise CredentialsError()
    if not user.user_auth:
        raise CredentialsError()
    if not verify_password(login_data.password, user.user_auth.hashed_password):
        raise CredentialsError()
    token = create_access_token({"sub": str(user.id), "role": user.role})

    return TokenResponse(access_token=token)


def registration_service(registration_data: RegistrationRequest, session: Session):
    statement = select(User).where(User.email == registration_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise EmailExistsError()

    new_user = User(
        full_name=registration_data.full_name,
        email=registration_data.email,
        phone=registration_data.phone,
        role=registration_data.role,
        # for testing conviniece created users are approved
        status=UserStatus.APPROVED,
    )
    session.add(new_user)
    session.flush()

    hashed_password = hash_password(registration_data.password)
    user_auth = UserAuth(user_id=new_user.id, hashed_password=hashed_password)
    session.add(user_auth)

    session.commit()
    session.refresh(new_user)
    return new_user


def change_my_password(
    session: Session, actor: User, user_id: UUID, data: ChangeMyPasswordRequest
):
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError()
    if actor.id != user.id:
        raise PermisionError()

    if not verify_password(data.current_password, user.user_auth.hashed_password):
        raise CredentialsError()

    user.user_auth.hashed_password = hash_password(data.new_password)
    session.add(user.user_auth)
    session.commit()
    return {"detail": "password changed successfully"}
