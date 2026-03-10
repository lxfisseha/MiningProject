from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from typing import Annotated

from starlette.datastructures import FormData

from src.auth.models import UserRole
from src.auth.services import get_user_by_id
from src.database import SESSION_DEP
from uuid import UUID

from .exceptions import InvalidRoleError
from .models import LicenseType
from .schemas import ProfileRegistrationRequest
from .services import create_user_profile
from .utils import nest_form_data


router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

@router.get("/register/{user_id}")
def register_profile(request: Request, user_id: UUID, session: SESSION_DEP):
    return templates.TemplateResponse(
        "auth/_register_profile.html",
        context={
            "request": request,
            "user": get_user_by_id(user_id, session),
            "roles": UserRole,
            "license_types": LicenseType,
        }
    )

@router.post("/register/{user_id}")
async def register_profile_post(request: Request, user_id: UUID, session: SESSION_DEP):
    #form_data = await request.form()
    #data = nest_form_data(dict(form_data))

    #profile = create_user_profile(ProfileRegistrationRequest(**data), session, user_id)
    return templates.TemplateResponse(
        'auth/partials/_profile_registration_success_response.html',
        {"request": request, "msg": "profile info saved", "user_id": user_id}
    )


@router.get("/file_upload_form/{user_id}")
async def file_upload_form(request: Request, user_id: UUID, session: SESSION_DEP):
    user = get_user_by_id(user_id, session)
    return templates.TemplateResponse(
        "auth/_file_upload_form.html",
        {"request": request,"user": user, "roles": UserRole}
    )

@router.post("/file_upload_form/{user_id}")
async def file_upload_form_post(request: Request, user_id: UUID, session: SESSION_DEP):
    return templates.TemplateResponse(
        'auth/partials/_file_upload_success_response.html',
        {"request": request, "msg": "file saved successfully", "user_id": user_id}
    )

@router.get("/registration_success")
async def registration_success(request: Request):
    return templates.TemplateResponse(
        "auth/partials/_registration_success_card.html",
        {"request": request}
    )
