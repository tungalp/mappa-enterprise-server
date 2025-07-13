
from typing import List
from uuid import UUID
from pydantic import BaseModel
from mapa.application.constants import Algorithms, ApplicationTypes, GrantTypes, LevelTypes

class CreateApi(BaseModel):
    name: str
    identifier: str
    signing_alg: str = Algorithms.Asymmetric.RS256
    level_type: str = LevelTypes.THIRD_PARTY
    

class CreateApiScope(BaseModel):
    name: str
    description: str
    api_id: UUID


class CreateClient(BaseModel):
    name: str
    client_id: str | None = None
    client_secret: str | None = None
    grant_types: List[str] | None = [GrantTypes.CLIENT_CREDENTIALS,
                                     GrantTypes.AUTHORIZATION_CODE, GrantTypes.REFRESH_TOKEN]
    redirect_uris: List[str] | None = None
    logout_uris: List[str] | None = None
    client_uri: str | None = None
    description: str | None = None
    application_type: str | None = ApplicationTypes.WEB
    logo_url: str | None = None
    token_endpoint_auth_method: str | None = None
    web_origins: List[str] | None = None
    cors_origins: List[str] | None = None
    require_consent: bool | None = True
    require_pkce: bool | None = False
    level_type: str | None = LevelTypes.THIRD_PARTY
    
    
class CreateClientApi(BaseModel):
    client_id: UUID
    api_id: UUID
