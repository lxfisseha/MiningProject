from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from typing import Annotated

from starlette.datastructures import FormData

from src.auth.models import UserRole, UserStatus
from src.auth.services import get_user_by_id
from src.database import SESSION_DEP
from uuid import UUID

from .exceptions import InvalidRoleError
from .models import LicenseType
from .schemas import ProfileRegistrationRequest, UserAndProfileUpdate, ProfileUpdateRequest
from .services import create_user_profile, get_user_with_profile, update_profile
from src.utils import nest_dotted_form_data
from src.auth.dependencies import CURRENT_USER_FROM_COOKIE
from src.requests.services import get_user_request_stats
from src.csrf_protection import generate_csrf_dependency

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

@router.get("/register/{user_id}")
def register_profile_stepper_form(request: Request, user_id: UUID, session: SESSION_DEP):
    return templates.TemplateResponse(
        "profiles/_register_profile.html",
        context={
            "request": request,
            "user": get_user_by_id(user_id, session),
            "roles": UserRole,
            "license_types": LicenseType,
        }
    )

@router.get('/incomplete/{user_id}')
def register_incomplete_profile(request: Request, user_id: UUID, session:SESSION_DEP):
    return templates.TemplateResponse(
        "profiles/registration_profile.html",
        context={
            "request": request,
            "user": get_user_by_id(user_id, session),
            "roles": UserRole,
            "license_types": LicenseType,
        }
    )


@router.post("/register/{user_id}")
async def register_profile_post(request: Request, user_id: UUID, session: SESSION_DEP):
    form_data = await request.form()
    data = nest_dotted_form_data(dict(form_data))

    profile = create_user_profile(ProfileRegistrationRequest(**data), session, user_id)
    return templates.TemplateResponse(
        'profiles/_registration_success_response_profile_.html',
        {"request": request, "msg": "profile info saved", "user_id": user_id}
    )


@router.get("/file_upload_form/{user_id}")
async def file_upload_form(request: Request, user_id: UUID, session: SESSION_DEP):
    user = get_user_by_id(user_id, session)
    return templates.TemplateResponse(
        "profiles/_file_upload_form.html",
        {"request": request,"user": user, "roles": UserRole}
    )

@router.post("/file_upload_form/{user_id}")
async def file_upload_form_post(request: Request, user_id: UUID, session: SESSION_DEP):
    data = await request.form()
    print(data)
    return templates.TemplateResponse(
        'profiles/_file_upload_success_response.html',
        {"request": request, "msg": "file saved successfully", "user_id": user_id}
    )

@router.get("/registration_success")
async def registration_success(request: Request):
    return templates.TemplateResponse(
        "profiles/_registration_success_card.html",
        {"request": request}
    )


@router.get("/me")
async def my_profile(
    request: Request, current_user: CURRENT_USER_FROM_COOKIE, session: SESSION_DEP, csrf: generate_csrf_dependency
):
    
    response = templates.TemplateResponse(
        request,
        "profiles/myprofile.html",
        context={
            "current_user": get_user_with_profile(current_user, session),
            "user_stats": get_user_request_stats(current_user, current_user.id, session),
            "user_documents": [],
            "user_status": UserStatus,
            "user_roles": UserRole,
            "license_types": LicenseType,
            "csrf_token": csrf.csrf_token
        },
    )

    csrf.save_signed_token_to_cookie(response)

    return response


@router.patch("/me")
async def edit_profile(request:Request, current_user: CURRENT_USER_FROM_COOKIE, session: SESSION_DEP):
    form_data = await request.form()
    data = ProfileUpdateRequest(**nest_dotted_form_data(dict(form_data)))
    update_profile(current_user, current_user.id, data, session)
    return templates.TemplateResponse("_success_alert.html", context={"request": request, "msg": "profile info edited successfully."})

