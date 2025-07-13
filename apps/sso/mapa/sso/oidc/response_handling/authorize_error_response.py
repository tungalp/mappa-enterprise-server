from pydantic import BaseModel


class AuthorizeErrorResponse(BaseModel):
    """Authorize ve Token servislerindeki hata modeli"""

    error: str
    error_description: str | None = None
    error_uri: str | None = None
    state: str | None = None

