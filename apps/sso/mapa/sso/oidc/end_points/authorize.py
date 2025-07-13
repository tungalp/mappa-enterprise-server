from typing import Optional
from pydantic import BaseModel, Field

from mapa.sso.constants import DisplayModes, ResponseModes


class AuthorizeEndpoint(BaseModel):
    """Authorize servis metodu parametreleri
    """
    # Authorization Code Flow
    response_type: str
    client_id: str
    redirect_uri: str
    state: Optional[str] = None
    audience: Optional[str] = None
    scope: Optional[str] = None
    prompt: Optional[str] = None
    response_mode: str = ResponseModes.QUERY

    connection: Optional[str] = None
    organization: Optional[str] = None
    invitation: Optional[str] = None

    # Authorization Code Flow with PKCE
    code_challenge_method: Optional[str] = None
    code_challenge: Optional[str] = None

    # Implicit Flow
    nonce: Optional[str] = None

    display: str = DisplayModes.PAGE
    max_age: int = 0
    ui_locales: Optional[str] = None
    id_token_hint: Optional[str] = None
    login_hint: Optional[str] = None
    screen_hint: Optional[str] = None
    acr_values: Optional[str] = None
    language: str | None
