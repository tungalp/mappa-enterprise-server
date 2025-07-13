from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from mapa.manage.constants import ApplicationTypes, LevelTypes
from mapa.manage.api_scope.api_scope_model import ApiScope
from mapa.manage.constants import Algorithms


class Api(BaseModel):
    """Api Modeli"""
    id: UUID
    name: str
    identifier: str
    allow_offline_access: bool | None = None
    skip_consent_for_verifiable_first_party_clients: str | None = None
    token_lifetime: int | None = None
    token_lifetime_for_web: int | None = None
    signing_alg: str = Algorithms.Asymmetric.RS256
    is_system: bool | None = None
    api_scopes: List[ApiScope] | None = None
    level_type: str = LevelTypes.THIRD_PARTY


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


class UpdateAllApi(UpdateApi):
    pass
