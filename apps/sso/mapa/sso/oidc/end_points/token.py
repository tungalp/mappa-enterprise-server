from typing import Optional
from pydantic import BaseModel


class TokenEndpoint(BaseModel):
    """Token servis metodu parametreleri
    """
    grant_type: str

    # Client
    client_id: str | None
    client_secret: str | None = None

    # Refresh Token
    refresh_token: str | None = None

    # Authorization Code Flow
    code: str | None = None
    redirect_uri: str | None = None
    audience: str | None = None
    code_verifier: str | None = None
