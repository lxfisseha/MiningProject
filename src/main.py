from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from .auth.exceptions import LoginError
from .exceptions import BaseException
from src.auth.routers import router as auth_routers
from src.profiles.routers import router as profile_routers
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates("templates")
app.include_router(auth_routers)
app.include_router(profile_routers)

@app.exception_handler(BaseException)
async def base_exception_handler_for_htmx(request: Request, exp: BaseException):
    return HTMLResponse(content=exp.message, status_code=200)

@app.exception_handler(LoginError)
async def login_error_handler_for_htmx(request:Request, exp: BaseException):
    return templates.TemplateResponse("auth/partials/_login_error_response.html", context={"request": request, "msg": exp.message})

@app.get("/")
def home():
    return "Hello world"
