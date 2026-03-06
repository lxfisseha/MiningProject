from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from .exceptions import CredentialsError, UserNotFoundError
from .utils import verify_access_token
from src.database import SESSION_DEP
from .models import User
from .models import UserStatus, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(session: SESSION_DEP, token: str = Depends(oauth2_scheme)):
    token_data = verify_access_token(token)

    user: User = session.get(User, token_data.id)
    if not user:
        raise UserNotFoundError()
    if user.role != token_data.role:
        raise CredentialsError()
    if user.status != UserStatus.APPROVED:
        raise CredentialsError()

    return user


def get_current_staff_or_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.STAFF, UserRole.ADMIN]:
        raise CredentialsError()
    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise CredentialsError()
    return current_user


CURRENT_USER_DEP = Annotated[User, Depends(get_current_user)]
CURRENT_STAFF_OR_ADMIN_DEP = Annotated[User, Depends(get_current_staff_or_admin)]
CURRENT_ADMIN_DEP = Annotated[User, Depends(get_current_admin)]
