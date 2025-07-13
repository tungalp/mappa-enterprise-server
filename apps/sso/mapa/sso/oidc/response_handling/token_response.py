from typing import List, Optional
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Token servis metodu dönüş modeli"""

    token_type: str = "bearer"
    expires_in: int
    tenant_id: str
    scope: str
    api_scopes: List[str]
    access_token: str | None = None
    id_token: str | None = None    
    refresh_token: str | None = None

    nonce: str | None = None
    language: str | None = None
