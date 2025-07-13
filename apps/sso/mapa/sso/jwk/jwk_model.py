from datetime import datetime
from typing import Any, Dict
from uuid import UUID  
from pydantic import BaseModel


class JwkModel(BaseModel):
    """JWKS Modeli"""

    id: UUID
    key_id: str
    private_pem: str
    public_pem: str
    jwk: Dict[str, Any]
    created_at: datetime
    expired_at: datetime

class CreateJwkModel(BaseModel):
    key_id: str
    private_pem: str
    public_pem: str    
    jwk: Dict[str, Any]
    expired_at: datetime


class UpdateJwkModel(BaseModel):
    ...


class UpdateAllJwkModel(UpdateJwkModel):
    ...
    