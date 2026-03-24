from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from uuid import UUID

from src.database import SESSION_DEP
from src.auth.dependencies import CURRENT_USER_FROM_COOKIE
from . import config

from .schemas import RequestFilters
from .services import get_my_requests, get_user_request_stats
from .enums import RequestStatus, RequestType, ConsultancyType, StudyLevel



router = APIRouter()
templates = Jinja2Templates(directory="templates")

request_type_to_form_map = {
    RequestType.CONSULTING: "requests/create_consulting_request_form.html",
    RequestType.LICENSE_SELL: "requests/create_license_sell_request_form.html",
    RequestType.MINERAL_BUYER: "requests/create_mineral_buy_request_form.html",
    RequestType.MINERAL_SELLER: "requests/create_mineral_sell_request_form.html",
    RequestType.OTHER: "requests/create_other_request_form.html"
}

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
            "allowed_requests_to_roles": config.ALLOWED_REQUEST_TYPES_TO_ROLES,
            "request_types":  RequestType
        },
    )


@router.get("/create_request_form/{request_type}")
def create_request_form(request: Request, request_type: RequestType, current_user: CURRENT_USER_FROM_COOKIE):
    form_template_path = _get_request_type_form(request_type)

    return templates.TemplateResponse(
        form_template_path,
        context={"request": request,
                 "current_user": current_user,
                 "consultancy_types": ConsultancyType,
                 "study_levels": StudyLevel
                 })

@router.get("/request_detail/{request_id}")
def request_detail(request_id: UUID):
    return "Request"

@router.get("/myrequests")
def my_requests():
    return "My Requests"

def _get_request_type_form(request_type: RequestType):
    form_template_path = request_type_to_form_map.get(request_type)
    if not form_template_path:
        form_template_path = request_type_to_form_map[RequestType.OTHER]
    return form_template_path

