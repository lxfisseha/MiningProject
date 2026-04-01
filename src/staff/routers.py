import time
from uuid import UUID

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

from src.auth.dependencies import CURRENT_STAFF_OR_ADMIN_FROM_COOKIE
from src.auth import models as auth_models
from src.auth import services as auth_services
from src.profiles import services as profile_services
from src.database import SESSION_DEP
from src.profiles.exceptions import InvalidRoleError

from .services import get_pending_users, change_user_status, get_users
from .schemas import UserFilters, UserSortOptions

router = APIRouter(prefix="/staff")
templates = Jinja2Templates(directory="templates")


role_to_template_name_map = {
    auth_models.UserRole.LICENSE_HOLDER: "staff/partials/_display_license_holder_profile_detail.html",
    auth_models.UserRole.EQUIPMENT_OWNER: "staff/partials/_display_equipment_owner_profile_detail.html",
    auth_models.UserRole.CONSULTANT: "staff/partials/_display_consultant_profile_detail.html",
    auth_models.UserRole.BUYER: "staff/partials/_display_buyer_profile_detail.html"
}

@router.get("/users/pending")
def get_pending_users_page(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
):
    return templates.TemplateResponse(
        "staff/pages/pending_users.html",
        context={
            "request": request,
            "current_user": current_user,
        },
    )

@router.get("/users/pending/table")
def get_pending_users_table(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
    session: SESSION_DEP,
    filters: Annotated[UserFilters, Query()],
):
    users = get_pending_users(current_user, session, filters)

    return templates.TemplateResponse(
        "staff/partials/_pending_users_table.html",
        {
            "request": request,
            "users": users,
        },
    )


@router.get("/users/")
def get_users_page(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
):
    return templates.TemplateResponse(
        "staff/pages/users.html",
        context={
            "request": request,
            "current_user": current_user,
            "user_roles": auth_models.UserRole,
            "user_status": auth_models.UserStatus,
            "sorting_options": UserSortOptions,
        },
    )


@router.get("/users/table")
def get_users_table(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
    session: SESSION_DEP,
    filters: Annotated[UserFilters, Query()],
):
    users = get_users(current_user, session, filters)
    return templates.TemplateResponse(
        "staff/partials/_users_table.html",
        {
            "request": request,
            "users": users,
            "user_status": auth_models.UserStatus,
            "users_count": len(users),
            "current_page": filters.current_page,
            
        },
    )

@router.get("/users/{user_id}")
def get_user_details_page(request:Request,
                          current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
                          user_id: UUID,
                          session: SESSION_DEP,
):
    user = auth_services.get_user_by_id(user_id, session)
    user_info = profile_services.get_user_with_profile(user, session)

    return templates.TemplateResponse(
        "staff/pages/user_details.html",
        {
            "request": request,
            "user_info": user_info,
            "user_status": auth_models.UserStatus,
            "user_roles": auth_models.UserRole,
            "get_profile_template_name": _get_profile_template_name,
        }
    )




@router.patch("users/{user_id}/approve")
def approve_user(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
    session: SESSION_DEP,
    user_id: UUID,
):
    change_user_status(current_user, session, user_id, auth_models.UserStatus.APPROVED)
    return HTMLResponse("Approved")


@router.patch("users/{user_id}/reject")
def reject_user(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
    session: SESSION_DEP,
    user_id: UUID,
):
    change_user_status(current_user, session, user_id, auth_models.UserStatus.REJECTED)
    return HTMLResponse("Rejected")

@router.patch("users/{user_id}/suspend")
def suspend_user(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
    session: SESSION_DEP,
    user_id: UUID,
):
    auth_services.change_user_status(current_user, session, user_id, auth_models.UserStatus.SUSPENDED)
    return HTMLResponse("Suspended")

def _get_profile_template_name(role: auth_models.UserRole) -> str:
    template_name = role_to_template_name_map.get(role, None)
    if not template_name:
        raise InvalidRoleError()
    return template_name
