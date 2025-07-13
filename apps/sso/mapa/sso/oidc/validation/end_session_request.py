from typing import Dict
from pydantic import BaseModel
from mapa.sso.user_session.user_session_model import UserSession


class EndSessionRequest(BaseModel):
    """Doğrulanmış EndSession isteği
    """
    user_session: UserSession
    post_logout_redirect_uri: str
    id_token_payload: Dict[str, str | float]
    state: str | None = None
