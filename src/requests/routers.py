from fastapi import APIRouter, Request, Query, Depends
from fastapi.templating import Jinja2Templates
from uuid import UUID
from typing import Annotated

from src.database import SESSION_DEP
from src.auth.dependencies import CURRENT_USER_FROM_COOKIE
from . import config
import time


from .schemas import RequestFilters, RequestCreate, RequestUpdate
from .services import (
    get_my_requests,
    get_user_request_stats,
    create_request,
    get_request_with_detail,
    update_request,
)
from .enums import RequestStatus, RequestType, ConsultancyType, StudyLevel
from src.profiles.models import LicenseType
from src.utils import nest_dotted_form_data

router = APIRouter()
templates = Jinja2Templates(directory="templates")

request_type_to_form_map = {
    RequestType.CONSULTING: "requests/create_consulting_request_form.html",
    RequestType.LICENSE_SELL: "requests/create_license_sell_request_form.html",
    RequestType.MINERAL_BUYER: "requests/create_mineral_buy_request_form.html",
    RequestType.MINERAL_SELLER: "requests/create_mineral_sell_request_form.html",
    RequestType.OTHER: "requests/create_other_request_form.html",
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
                RequestFilters(limit=15, offset=0),
            ),
            "user_stats": get_user_request_stats(
                current_user, current_user.id, session
            ),
            "request_status": RequestStatus,
            "allowed_requests_to_roles": config.ALLOWED_REQUEST_TYPES_TO_ROLES,
            "request_types": RequestType,
        },
    )


@router.get("/create_request_form/{request_type}")
def create_request_form(
    request: Request, request_type: RequestType, current_user: CURRENT_USER_FROM_COOKIE
):
    form_template_path = _get_request_type_form(request_type)

    return templates.TemplateResponse(
        form_template_path,
        context={
            "request": request,
            "current_user": current_user,
            "consultancy_types": ConsultancyType,
            "study_levels": StudyLevel,
            "license_types": LicenseType,
            "request_types": RequestType,
        },
    )


@router.post("/create_request/{request_type}")
async def create_request_post(
    request: Request,
    request_type: RequestType,
    current_user: CURRENT_USER_FROM_COOKIE,
    session: SESSION_DEP,
):
    form_data = await request.form()
    data = RequestCreate(
        request_type=request_type, **nest_dotted_form_data(dict(form_data))
    )
    create_request(session, data, current_user)

    return templates.TemplateResponse(
        "requests/_request_created_alert.html",
        context={"request": request, "msg": "Request created successfully!"},
    )


@router.patch("/update_request/{request_id}")
async def update_request_patch(
    request: Request,
    request_id: UUID,
    session: SESSION_DEP,
    current_user: CURRENT_USER_FROM_COOKIE,
):
    form_data = await request.form()
    data = RequestUpdate(**nest_dotted_form_data(dict(form_data)))
    update_request(session, request_id, data, current_user)

    return templates.TemplateResponse(
        "_success_alert.html",
        {"request": request, "msg": "Request updated successfully."},
    )


@router.get("/request_detail/{request_id}")
def request_detail(
    request: Request,
    request_id: UUID,
    session: SESSION_DEP,
    current_user: CURRENT_USER_FROM_COOKIE,
):
    return templates.TemplateResponse(
        "requests/request_detail.html",
        context={
            "request": request,
            "request_info": get_request_with_detail(session, request_id, current_user),
            "current_user": current_user,
            "request_types": RequestType,
            "consultancy_types": ConsultancyType,
            "study_levels": StudyLevel,
            "license_types": LicenseType,
        },
    )


@router.get("/myrequests")
def my_requests(
    request: Request, current_user: CURRENT_USER_FROM_COOKIE, session: SESSION_DEP
):
    return templates.TemplateResponse(
        "requests/my_requests.html",
        {
            "request": request,
            "current_user": current_user,
            "request_types": RequestType,
            "user_stats": get_user_request_stats(
                current_user, current_user.id, session
            ),
            "allowed_requests_to_roles": config.ALLOWED_REQUEST_TYPES_TO_ROLES,
        },
    )


@router.get("/requests_table")
async def requests_table(
    request: Request,
    session: SESSION_DEP,
    current_user: CURRENT_USER_FROM_COOKIE,
    filters: RequestFilters = Depends(),
):

    time.sleep(0.5)
    requests = get_my_requests(session, current_user, filters)

    return templates.TemplateResponse(
        "requests/_requests_table.html",
        {
            "request": request,
            "requests": requests,
            "current_user": current_user,
            "request_types": RequestType,
            "request_status": RequestStatus,
            "filters": filters,
        },
    )


def _get_request_type_form(request_type: RequestType):
    form_template_path = request_type_to_form_map.get(request_type)
    if not form_template_path:
        form_template_path = request_type_to_form_map[RequestType.OTHER]
    return form_template_path
