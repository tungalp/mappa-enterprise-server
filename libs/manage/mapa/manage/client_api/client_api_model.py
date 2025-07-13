from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from mapa.manage.api.api_model import Api
from mapa.manage.api_scope.api_scope_model import ApiScope
from mapa.manage.client.client_model import Client


class ClientApi(BaseModel):
    """ClientApi Modeli"""
    id: UUID
    client_id: UUID
    client: Client | None = None
    api_id: UUID
    api: Api | None = None
    api_scopes: List[ApiScope] | None = None

class CreateClientApi(BaseModel):
    client_id: UUID
    api_id: UUID

class UpdateClientApi(BaseModel):
    pass

class UpdateAllClientApi(UpdateClientApi):
    pass
