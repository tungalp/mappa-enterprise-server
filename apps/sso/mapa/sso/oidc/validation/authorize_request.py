from typing import List, Optional

from pydantic import BaseModel
from mapa.sso.models import Client
from mapa.sso.constants import DisplayModes, ResponseModes, StandardScopes
from mapa.sso.user_session.user_session_model import UserSession


class AuthorizeRequest(BaseModel):
    """Doğrulanmış Authorize isteği
    """
    user_session: UserSession | None = None
    client: Client
    redirect_uri: str
    response_types: List[str]
    audience: str | None = None
    scopes: List[str] = []
    prompt_modes: List[str] = []
    response_mode: str = ResponseModes.QUERY
    max_age: int = 0
    state: str | None = None    

    # Authorization Code Flow
    connection: str | None = None
    organization: str | None = None
    invitation: str | None = None

    # Authorization Code Flow with PKCE
    code_challenge_method: str | None = None
    code_challenge: str | None = None

    # Implicit Flow
    nonce: str | None = None

    display: str = DisplayModes.PAGE
    ui_locales: str | None = None
    id_token_hint: str | None = None
    login_hint: str | None = None
    screen_hint: Optional[str] = None
    acr_values: str | None = None

    is_openid: bool = StandardScopes.OPENID in scopes

    grant_type: str | None = None
