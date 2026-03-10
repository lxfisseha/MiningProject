from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.database import SESSION_DEP
from typing import Annotated


from fastapi import APIRouter, Request, Form

from .models import UserRole
from .services import login_service, registration_service
from .schemas import LoginRequest, UserResponse, RegisterUserRequest
from .utils import save_token_response_to_cookies, nest_dotted_form_data

router = APIRouter()

templates = Jinja2Templates(directory="templates")

client_roles = [
    UserRole.LICENSE_HOLDER.value,
    UserRole.EQUIPMENT_OWNER.value,
    UserRole.CONSULTANT.value,
    UserRole.BUYER.value,
]


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/register")
async def register(
    request: Request,
):
    return templates.TemplateResponse(
        "auth/register_user.html", {"request": request, "roles": client_roles}
    )


@router.post("/login")
async def login_post(
    login_data: Annotated[LoginRequest, Form()],
    session: SESSION_DEP,
):
    token = login_service(login_data, session)
    response = HTMLResponse()

    save_token_response_to_cookies(response, token)

    response.headers["HX-Redirect"] = "/"
    return response





@router.post("/register")
async def register(request: Request, session: SESSION_DEP):
    form_data = await request.form()

    registration_request = RegisterUserRequest(**dict(form_data))
    new_user = registration_service(registration_request, session)

    return templates.TemplateResponse(
        "auth/partials/_registration_success_response.html",
        {"request": request, "msg": "user registered successfully!", "user_id": new_user.id},
    )
