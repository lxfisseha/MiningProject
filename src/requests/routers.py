from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from uuid import UUID

from src.database import SESSION_DEP
from src.auth.dependencies import CURRENT_USER_FROM_COOKIE
from .config import ALLOWED_REQUESTS_TO_ROLES

from .schemas import RequestFilters
from .services import get_my_requests, get_user_request_stats
from .enums import RequestStatus, RequestType



router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def home_page(
    request: Request,
    current_user: CURRENT_USER_FROM_COOKIE,
    session: SESSION_DEP,
):
    return templates.TemplateResponse(
        "requests/home.html",
        context={
            "request": request,
            "current_user": current_user,
            "requests": get_my_requests(
                session,
                current_user,
                RequestFilters(limit=10, offset=0),
            ),
            "user_stats": get_user_request_stats(current_user, current_user.id, session),
            "request_status": RequestStatus,
            "allowed_requests_to_roles": ALLOWED_REQUESTS_TO_ROLES,
            "request_types":  RequestType
        },
    )

@router.get("/myrequests")
def my_requests():
    return "My Requests"

@router.get("/create_request_form")
def create_request_form():
    return "Form"

@router.get("/request_detail/{request_id}")
def request_detail(request_id: UUID):
    return "Request"
