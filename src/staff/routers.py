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
from src.requests import models as request_models
from src.requests import services as request_services
from src.requests.enums import RequestStatus, RequestType
from src.requests.routers import _get_request_type_info_card_template_name
from src.csrf_protection import generate_csrf_dependency

from .services import get_pending_users, change_user_status, get_total_users_count, get_users, get_all_requests, get_total_requests_count
from .schemas import UserFilters, UserSortOptions, RequestsFilters

router = APIRouter(prefix="/staff")
templates = Jinja2Templates(directory="templates")


role_to_template_name_map = {
    auth_models.UserRole.LICENSE_HOLDER: "staff/partials/_display_license_holder_profile_detail.html",
    auth_models.UserRole.EQUIPMENT_OWNER: "staff/partials/_display_equipment_owner_profile_detail.html",
    auth_models.UserRole.CONSULTANT: "staff/partials/_display_consultant_profile_detail.html",
    auth_models.UserRole.BUYER: "staff/partials/_display_buyer_profile_detail.html"
}





@router.get("/requests/all")
def get_all_requests_page(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE
):
    response = templates.TemplateResponse(
        "staff/pages/requests.html",
        context={
            "request": request,
            "current_user": current_user,
            "request_types": RequestType,
            "request_status": RequestStatus
        },
    )
    return response

@router.get("/requests/all/table")
def get_all_requests_table(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
    filters: Annotated[RequestsFilters, Query()],
    session: SESSION_DEP,
):
    time.sleep(1)  # Simulate loading time
    requests = get_all_requests(current_user, session, filters)
    requests_count = get_total_requests_count(current_user, session, filters)
    return templates.TemplateResponse(
        "staff/partials/_requests_table.html",
        context={
            "request": request,
            "current_user": current_user,
            "requests": requests,
            "requests_count": requests_count,
            "request_status": RequestStatus,
            "current_page": filters.current_page,

        },
    )

@router.get("/users/pending")
def get_pending_users_page(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
    csrf: generate_csrf_dependency
):
    
    response = templates.TemplateResponse(
        "staff/pages/pending_users.html",
        context={
            "request": request,
            "current_user": current_user,
            "csrf_token": csrf.csrf_token
        },
    )

    csrf.save_signed_token_to_cookie(response)
    return response

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
    csrf: generate_csrf_dependency
):
    response = templates.TemplateResponse(
        "staff/pages/users.html",
        context={
            "request": request,
            "current_user": current_user,
            "user_roles": auth_models.UserRole,
            "user_status": auth_models.UserStatus,
            "sorting_options": UserSortOptions,
            "csrf_token": csrf.csrf_token
        },
    )

    csrf.save_signed_token_to_cookie(response)
    return response



@router.get("/users/table")
def get_users_table(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
    session: SESSION_DEP,
    filters: Annotated[UserFilters, Query()],
):
    users = get_users(current_user, session, filters)
    users_count = get_total_users_count(current_user, session, filters)
    return templates.TemplateResponse(
        "staff/partials/_users_table.html",
        {
            "request": request,
            "users": users,
            "user_status": auth_models.UserStatus,
            "users_count": users_count,
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


@router.get("/requests/{request_id}")
def get_request_detail_page(
    request: Request,
    current_user: CURRENT_STAFF_OR_ADMIN_FROM_COOKIE,
    request_id: UUID,
    session: SESSION_DEP,
):
    request_info = request_services.get_request_with_detail(session, request_id, current_user)
    return templates.TemplateResponse(
        "staff/pages/request_details.html",
        context={
            "request": request,
            "current_user": current_user,
            "request_info": request_info,
            "request_status": RequestStatus,
            "request_type": RequestType,
            "info_card_template_name": _get_request_type_info_card_template_name(request_info.request_type)
        },
    )   

def _get_profile_template_name(role: auth_models.UserRole) -> str:
    template_name = role_to_template_name_map.get(role, None)
    if not template_name:
        raise InvalidRoleError()
    return template_name
