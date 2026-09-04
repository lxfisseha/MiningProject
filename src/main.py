from fastapi import Depends, FastAPI, Request
from starlette.responses import RedirectResponse
from pydantic_core import ValidationError
from sqlmodel import SQLModel

from .auth.exceptions import (
    LoginRequiredError,
)

from .auth.schemas import LoginRequest
from .exceptions import BaseException, validation_exception_handler
from .auth.routers import router as auth_router
from .profiles.routers import router as profiles_router
from .requests.routers import router as requests_router
from .staff.routers import router as staff_router
from .documents.routers import router as docs_router
from fastapi.templating import Jinja2Templates

from .profiles.exceptions import IncompleteRegistrationProfileNotFoundError
from .rate_limiting import limiter, rate_limit_handler


from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from .csrf_protection import CSRFValidationError, csrf_validation_exception_handler, csrf_protect
from .database import engine
from .seed import seed_demo_users


class HTTPSForceMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["scheme"] = "https"
        return await self.app(scope, receive, send)


fastapi_app = FastAPI(dependencies=[Depends(csrf_protect)])

templates = Jinja2Templates("templates")

fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
fastapi_app.add_middleware(SlowAPIMiddleware)


@fastapi_app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    seed_demo_users()


fastapi_app.include_router(auth_router)
fastapi_app.include_router(profiles_router)
fastapi_app.include_router(requests_router)
fastapi_app.include_router(staff_router)
fastapi_app.include_router(docs_router)

fastapi_app.add_exception_handler(ValidationError, validation_exception_handler)
fastapi_app.add_exception_handler(CSRFValidationError, csrf_validation_exception_handler)


@fastapi_app.exception_handler(LoginRequiredError)
async def redirect_to_login(request: Request, exp: LoginRequiredError):
    return RedirectResponse(url="/login", status_code=303)

@fastapi_app.exception_handler(IncompleteRegistrationProfileNotFoundError)
async def incomplete_registration_profile_not_found_handler(
    request: Request, exp: IncompleteRegistrationProfileNotFoundError
):
    return RedirectResponse(url=f"incomplete/{exp.user_id}", status_code=303)

@fastapi_app.exception_handler(BaseException)
async def base_exception_handler(request: Request, exp: BaseException):
    return templates.TemplateResponse(
        "_error_alert.html", context={"request": request, "msg": exp.message}
    )


app = HTTPSForceMiddleware(fastapi_app)
