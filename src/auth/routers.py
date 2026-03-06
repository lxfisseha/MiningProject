from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.database import SESSION_DEP
from .services import registration_service, login_service
from .schemas import UserResponse, RegistrationRequest
from .models import UserRole
from .dependencies import CURRENT_USER_DEP
from .utils import save_token_response_to_cookies


router = APIRouter(
    prefix="/auth",
    tags=[
        "Auth",
    ],
)


templates = Jinja2Templates(directory="templates")


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("/auth/login.html", {"request": request})


@router.post("/login")
async def login_post(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SESSION_DEP,
):
    token = login_service(login_data, session)
    return save_token_response_to_cookies(token)


@router.get("/register")
async def registration_form(
    request: Request,
):
    return templates.TemplateResponse(
        "auth/register.html", {"request": request, "roles": UserRole}
    )


@router.post("/register")
async def register(
    request: Request, session: SESSION_DEP, data: Annotated[RegistrationRequest, Form()]
):

    registration_service(data, session)

    return templates.TemplateResponse(
        "partials/registration_success.html",
        {"request": request},
        headers={
            "HX-Retarget": "#register-card",
            "HX-Reswap": "outerHTML",
        },
    )
