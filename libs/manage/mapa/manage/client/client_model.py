from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from pydantic import BaseModel
from mapa.manage.constants import ApplicationTypes, GrantTypes, LevelTypes
from nanoid import generate


class Client(BaseModel):
    """Client Modeli"""
    id: UUID
    name: str
    client_id: str | None = None
    client_secret: str | None = None
    redirect_uris: List[str] | None = None
    logout_uris: List[str] | None = None
    client_uri: str | None = None
    description: str | None = None
    application_type: str = ApplicationTypes.WEB
    logo_url: str | None = None
    token_endpoint_auth_method: str | None = None
    web_origins: List[str] | None = None
    cors_origins: List[str] | None = None
    require_consent: bool = True
    is_system: bool = False
    require_pkce: bool = False
    grant_types: List[str]
    level_type: str = LevelTypes.THIRD_PARTY
    id_token_lifetime: int | None = None
    access_token_lifetime: int | None = None
    authorization_code_lifetime: int | None = None
    absolute_refresh_token_lifetime: int | None = None
    sliding_refresh_token_lifetime: int | None = None
    device_code_lifetime: int | None = None
    ciba_lifetime: int | None = None

    refresh_token_rotation: bool | None = None

    jwt_signature_algorithm: str | None = None
    organizations: List[Any]  | None = None

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


class UpdateClient(BaseModel):
    name: str | None = None
    grant_types: List[str] | None = None
    redirect_uris: List[str] | None = None
    logout_uris: List[str] | None = None
    client_uri: str | None = None
    description: str | None = None
    application_type: str | None = None
    logo_url: str | None = None
    token_endpoint_auth_method: str | None = None
    web_origins: List[str] | None = None
    cors_origins: List[str] | None = None
    require_consent: bool | None = None
    require_pkce: bool | None = None


class UpdateAllClient(UpdateClient):
    pass


class ClientInfo(BaseModel):
    client_id: str
    name: str
    level_type: str
    description: str | None = None
    logo_url: str | None = None
