import time

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from starlette.responses import RedirectResponse

from ..database import SESSION_DEP
from typing import Annotated


from fastapi import APIRouter, Request, Form

from .dependencies import CURRENT_USER_FROM_COOKIE
from .models import UserRole
from .services import (
    login_service,
    registration_service,
    change_my_password,
    update_user,
)
from .schemas import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    RegisterUserRequest,
    ChangeMyPasswordRequest,
    UserUpdate,
)

from .utils import create_access_token, save_token_response_to_cookies

from src.csrf_protection import generate_csrf_dependency, csrf_protect

router = APIRouter()

templates = Jinja2Templates(directory="templates")

client_roles = [
    UserRole.LICENSE_HOLDER.value,
    UserRole.EQUIPMENT_OWNER.value,
    UserRole.CONSULTANT.value,
    UserRole.BUYER.value,
]


@router.get("/login")
async def login(request: Request, csrf: generate_csrf_dependency):
    response = templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "csrf_token": csrf.csrf_token}
    )

    csrf.save_signed_token_to_cookie(response)
    
    return response


@router.get("/register")
async def register(
    request: Request,
    csrf: generate_csrf_dependency
):
    response = templates.TemplateResponse(
        "auth/registration.html", {"request": request, "roles": client_roles, "csrf_token": csrf.csrf_token}
    )

    csrf.save_signed_token_to_cookie(response)
    return response


@router.post("/login")
async def login_post(
    login_data: Annotated[LoginRequest, Form()],
    session: SESSION_DEP,
):
    user = login_service(login_data, session)
    token = create_access_token({"sub": str(user.id), "role": user.role})

    response = HTMLResponse()

    save_token_response_to_cookies(response, TokenResponse(access_token=token))

    if user.is_staff_or_admin:
        response.headers["HX-Redirect"] = "/staff/users/pending"
    else:
        response.headers["HX-Redirect"] = "/"
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    response.delete_cookie("token_type")
    return response


@router.post("/register")
async def register(request: Request, session: SESSION_DEP):
    form_data = await request.form()

    registration_request = RegisterUserRequest(**dict(form_data))
    new_user = registration_service(registration_request, session)

    return templates.TemplateResponse(
        "auth/partials/_registration_success_response.html",
        {
            "request": request,
            "msg": "user registered successfully!",
            "user_id": new_user.id,
        },
    )


@router.patch("/me")
async def edit_user(
    request: Request, current_user: CURRENT_USER_FROM_COOKIE, session: SESSION_DEP
):
    form_data = await request.form()
    data = UserUpdate(**dict(form_data))
    time.sleep(1)

    update_user(current_user, current_user.id, data, session)

    return templates.TemplateResponse(
        "_success_alert.html",
        context={"request": request, "msg": "user updated successfully."},
    )


@router.post("/change_password")
async def change_password(
    request: Request, current_user: CURRENT_USER_FROM_COOKIE, session: SESSION_DEP
):
    form_data = await request.form()
    data = ChangeMyPasswordRequest(**dict(form_data))

    change_my_password(session, current_user, current_user.id, data)

    return templates.TemplateResponse(
        "_success_alert.html",
        context={"request": request, "msg": "password changed successfully!"},
    )
