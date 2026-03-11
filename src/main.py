from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from .auth.exceptions import LoginError, RegistrationErrorBase, UnApprovedUserErrorLogin, LoginRequiredError, \
    EditProfileError
from .auth.schemas import LoginRequest
from .exceptions import BaseException
from src.auth.routers import router as auth_router
from src.profiles.routers import router as profiles_router
from src.requests.routers import router as requests_router
from fastapi.templating import Jinja2Templates

from .profiles.exceptions import IncompleteRegistrationProfileNotFoundError

app = FastAPI()

templates = Jinja2Templates("templates")
app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(requests_router)

@app.exception_handler(LoginRequiredError)
async def redirect_to_login(request: Request, exp: LoginRequiredError):
    return RedirectResponse(url="/login", status_code=303)

@app.exception_handler(IncompleteRegistrationProfileNotFoundError)
async def incomplete_registration_profile_not_found_handler(request: Request, exp: IncompleteRegistrationProfileNotFoundError):
    return RedirectResponse(url=f"incomplete/{exp.user_id}", status_code=303)

@app.exception_handler(BaseException)
async def base_exception_handler(request: Request, exp: BaseException):
    return templates.TemplateResponse("_error_alert.html", context={"request": request, "msg": exp.message})

@app.get("/")
def home():
    return "Hello world"
