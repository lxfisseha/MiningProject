import time
from uuid import UUID

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

from src.auth.dependencies import CURRENT_STAFF_OR_ADMIN_FROM_COOKIE
from src.auth import models as auth_models
from src.database import SESSION_DEP

from .services import get_pending_users, change_user_status
from .schemas import UserFilters

router = APIRouter(prefix="/staff")
templates = Jinja2Templates(directory="templates")


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
    time.sleep(1)
    users = get_pending_users(current_user, session, filters)

    return templates.TemplateResponse(
        "staff/partials/_pending_users_table.html",
        {
            "request": request,
            "users": users,
        },
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
