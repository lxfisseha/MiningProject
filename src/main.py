from fastapi import Depends, FastAPI, Request
from starlette.responses import RedirectResponse
from pydantic_core import ValidationError

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

app = FastAPI(dependencies=[Depends(csrf_protect)])

templates = Jinja2Templates("templates")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)


app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(requests_router)
app.include_router(staff_router)
app.include_router(docs_router)

app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(CSRFValidationError, csrf_validation_exception_handler)


@app.exception_handler(LoginRequiredError)
async def redirect_to_login(request: Request, exp: LoginRequiredError):
    return RedirectResponse(url="/login", status_code=303)

@app.exception_handler(IncompleteRegistrationProfileNotFoundError)
async def incomplete_registration_profile_not_found_handler(
    request: Request, exp: IncompleteRegistrationProfileNotFoundError
):
    return RedirectResponse(url=f"incomplete/{exp.user_id}", status_code=303)

@app.exception_handler(BaseException)
async def base_exception_handler(request: Request, exp: BaseException):
    return templates.TemplateResponse(
        "_error_alert.html", context={"request": request, "msg": exp.message}
    )
