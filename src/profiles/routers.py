from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.auth.models import UserRole
from src.profiles.models import LicenseType

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

@router.get("/register")
def register_profile(request: Request):
    return templates.TemplateResponse(
        "auth/register_profile.html",
        context={
            "request": request,
            "roles": UserRole,
            "license_types": LicenseType,
            "role": UserRole.LICENSE_HOLDER
        }
    )
