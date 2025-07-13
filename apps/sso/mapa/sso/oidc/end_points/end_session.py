from typing import Optional
from pydantic import BaseModel


class EndSessionEndpoint(BaseModel):
    """EndSession servis metodu parametreleri
    """
    id_token_hint: str
    post_logout_redirect_uri: str
    state: str | None = None
