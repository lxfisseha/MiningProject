from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from pydantic_core import ValidationError
from fastapi import Request


class BaseException(HTTPException):
    def __init__(self, status_code: int, message: str, *args):
        super().__init__(status_code, message, *args)
        self.message = message
    
    @property
    def detail(self):
        return self.message
    
    @detail.setter
    def detail(self, value):
        self.message = value
    

class PermisionError(BaseException):
    def __init__(self, status_code: int = 401, message="permision denied.", *args):
        super().__init__(status_code, message, *args)

async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = exc.errors()

    # Build HTML list of errors
    error_items = ""
    for err in errors:
        field = err["loc"][-1]
        message = err["msg"]

        error_items += f"""
        <li>
            <strong>{field}</strong>: {message}
        </li>
        """

    html_content = f"""
                <div class="alert alert-danger  mb-0 pt-3 border-0">
                        
                            <i class="bi bi-exclamation-octagon-fill me-2"></i>
                            Validation Error </br>

                        <ul class="text-danger">
                            {error_items}
                        </ul>
                </div>
    """

    return HTMLResponse(content=html_content, status_code=200)
