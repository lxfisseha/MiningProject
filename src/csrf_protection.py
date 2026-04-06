from fastapi import Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi_csrf_protect import CsrfProtect
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Annotated

from .exceptions import BaseException


class CsrfSettings(BaseSettings):
  secret_key: str = "asecrettoeverybody"
  cookie_samesite: str = "none"
  cookie_secure: bool = True

class CSRFToken(BaseModel):
    csrf_token: str
    signed_token: str
    csrf_protect: CsrfProtect

    class Config:
        arbitrary_types_allowed=True
    
    def save_signed_token_to_cookie(self,response: Response):
        self.csrf_protect.set_csrf_cookie(self.signed_token, response)
        return 1

class CSRFValidationError(BaseException):
    def __init__(self, status_code: int = 403, message="CSRF validation failed.", *args):
        super().__init__(status_code, message, *args)


SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


@CsrfProtect.load_config
def get_csrf_config():
  return CsrfSettings()

async def csrf_protect(
    request: Request,
    response: Response,
    csrf_protect: CsrfProtect = Depends(),
):
    if request.method in SAFE_METHODS:
        return
    try:
        await csrf_protect.validate_csrf(request)
        csrf_protect.unset_csrf_cookie(response) 
    except Exception as e:
        raise CSRFValidationError()

def generate_csrf(
    csrf_protect: CsrfProtect = Depends(),
) -> CSRFToken:
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    return CSRFToken(csrf_token=csrf_token, signed_token=signed_token, csrf_protect=csrf_protect)

async def csrf_validation_exception_handler(request: Request, exp: CSRFValidationError):
    return HTMLResponse(content=f"""
        <div class="alert alert-danger  mb-0 pt-3 border-0">
                
                    <i class="bi bi-exclamation-octagon-fill me-2"></i>
                    {exp.message}
        </div>
    """, status_code=203)

generate_csrf_dependency = Annotated[CSRFToken, Depends(generate_csrf)]