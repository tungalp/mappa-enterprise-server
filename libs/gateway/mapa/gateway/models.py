
from typing import List
from uuid import UUID
from pydantic import BaseModel
from mapa.gateway.constant import Algorithms, LevelTypes

class CreateApi(BaseModel):
    name: str
    identifier: str
    signing_alg: str = Algorithms.Asymmetric.RS256
    level_type: str = LevelTypes.THIRD_PARTY
    
    
class UpdateApi(BaseModel):
    name: str | None = None
    token_lifetime: int | None = None
    allow_offline_access: bool | None = None
    skip_consent_for_verifiable_first_party_clients: str | None = None
    token_lifetime_for_web: int | None = None
    signing_alg: str | None = None
    
    
class ApiScope(BaseModel):
    id: UUID
    name: str
    description: str
    api_id: UUID
    
    
class CreateApiScope(BaseModel):
    name: str
    description: str
    api_id: UUID
