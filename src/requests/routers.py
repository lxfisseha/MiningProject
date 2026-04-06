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
from src.csrf_protection import generate_csrf_dependency

router = APIRouter()
templates = Jinja2Templates(directory="templates")

request_type_to_templates_map = {
    RequestType.CONSULTING: {
        "create_form": "requests/partials/_create_consulting_request_form.html",
        "edit_form": "requests/partials/_edit_request_modal_consulting.html",
        "info_card": "requests/partials/_request_info_card_consulting.html",
    },
    RequestType.LICENSE_SELL: {
        "create_form": "requests/partials/_create_license_sell_request_form.html",
        "edit_form": "requests/partials/_edit_request_modal_license_sell.html",
        "info_card": "requests/partials/_request_info_card_license_sell.html",
    },
    RequestType.MINERAL_BUYER: {
        "create_form": "requests/partials/_create_mineral_buy_request_form.html",
        "edit_form": "requests/partials/_edit_request_modal_mineral_buy.html",
        "info_card": "requests/partials/_request_info_card_mineral_buy.html",
    },
    RequestType.MINERAL_SELLER: {
        "create_form": "requests/partials/_create_mineral_sell_request_form.html",
        "edit_form": "requests/partials/_edit_request_modal_mineral_sell.html",
        "info_card": "requests/partials/_request_info_card_mineral_sell.html",
    },
    RequestType.OTHER: {
        "create_form": "requests/partials/_create_other_request_form.html",
        "edit_form": "requests/partials/_edit_request_modal_other.html",
        "info_card": "requests/partials/_request_info_card_other.html",
    },
}


@router.get("/")
async def home_page(
    request: Request,
    current_user: CURRENT_USER_FROM_COOKIE,
    session: SESSION_DEP,
):
    return templates.TemplateResponse(
        "requests/pages/home.html",
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
    request: Request, request_type: RequestType, current_user: CURRENT_USER_FROM_COOKIE, csrf:  generate_csrf_dependency
):

    response = templates.TemplateResponse(
        "requests/pages/create_request.html",
        context={
            "request": request,
            "current_user": current_user,
            "consultancy_types": ConsultancyType,
            "study_levels": StudyLevel,
            "license_types": LicenseType,
            "request_types": RequestType,
            "request_type": request_type,
            "request_form_template_name": _get_request_type_create_form_template_name(
                request_type
            ),
            "csrf_token": csrf.csrf_token
        },
    )

    csrf.save_signed_token_to_cookie(response)
    return response


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
        "_success_alert.html",
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
    csrf: generate_csrf_dependency
):
    request_info = get_request_with_detail(session, request_id, current_user)
    response = templates.TemplateResponse(
        "requests/pages/request_detail.html",
        context={
            "request": request,
            "request_info": request_info,
            "current_user": current_user,
            "request_types": RequestType,
            "consultancy_types": ConsultancyType,
            "study_levels": StudyLevel,
            "license_types": LicenseType,
            "info_card_template_name": _get_request_type_info_card_template_name(
                request_info.request_type
            ),
            "edit_modal_template_name": _get_request_type_edit_form_template_name(
                request_info.request_type
            ),
            "csrf_token": csrf.csrf_token
        },
    )

    csrf.save_signed_token_to_cookie(response)

    return response

@router.get("/myrequests")
def my_requests(
    request: Request, current_user: CURRENT_USER_FROM_COOKIE, session: SESSION_DEP
):
    return templates.TemplateResponse(
        "requests/pages/my_requests.html",
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
        "requests/partials/_requests_table.html",
        {
            "request": request,
            "requests": requests,
            "current_user": current_user,
            "request_types": RequestType,
            "request_status": RequestStatus,
            "filters": filters,
        },
    )


def _get_request_type_create_form_template_name(request_type: RequestType):
    templates = (
        request_type_to_templates_map.get(request_type)
        or request_type_to_templates_map[RequestType.OTHER]
    )

    return (
        templates.get("create_form")
        or request_type_to_templates_map[RequestType.OTHER]["create_form"]
    )


def _get_request_type_edit_form_template_name(request_type: RequestType):
    templates = (
        request_type_to_templates_map.get(request_type)
        or request_type_to_templates_map[RequestType.OTHER]
    )

    return (
        templates.get("edit_form")
        or request_type_to_templates_map[RequestType.OTHER]["edit_form"]
    )


def _get_request_type_info_card_template_name(request_type: RequestType):
    templates = (
        request_type_to_templates_map.get(request_type)
        or request_type_to_templates_map[RequestType.OTHER]
    )

    return (
        templates.get("info_card")
        or request_type_to_templates_map[RequestType.OTHER]["info_card"]
    )
