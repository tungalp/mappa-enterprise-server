from typing import Optional
from pydantic import BaseModel


class AuthorizeResponse(BaseModel):
    """Authorize servis metodu dönüş modeli"""

    issuer: str | None = None
    identity_token: str | None = None
    access_token: str | None = None
    access_token_lifetime: str | None = None
    code: str | None = None
    session_state: str | None = None
    state: str | None = None
    language: str | None = None
