from datetime import datetime, timezone, timedelta
from fastapi.responses import HTMLResponse
from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError
import jwt

from .exceptions import CredentialsError
from .config import settings as config
from .schemas import TokenResponse, TokenData


password_hash = PasswordHash.recommended()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_SECRET_KEY, algorithm=config.ALGORITHM
    )

    return encoded_jwt


def verify_access_token(token) -> TokenData:
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        id = payload.get("sub")
        role = payload.get("role")
        if id is None:
            raise CredentialsError("Could not validate credentials. id not found")
        token_data = TokenData(id=id, role=role)
        return token_data
    except InvalidTokenError:
        raise CredentialsError("Could not validate credentials.")


def hash_password(password):
    return password_hash.hash(password)


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def save_token_response_to_cookies(response:HTMLResponse ,token: TokenResponse):
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        secure=True,  # True in production (HTTPS)
        samesite="lax",
    )
    response.set_cookie(
        key="token_type",
        value=token.token_type,
        httponly=True,
        secure=True,  # True in production (HTTPS)
        samesite="lax",
    )
    return response

