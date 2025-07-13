from uuid import UUID
from pydantic import BaseModel
from mapa.sso.refresh_token.refresh_token_model import RefreshToken
from mapa.sso.models import Client

class RevocationRequest(BaseModel):
    """Doğrulanmış Token isteği
    """
    client: Client
    token: str
    token_type_hint: str
    refresh_token: RefreshToken
