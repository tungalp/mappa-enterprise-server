from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from mapa.manage.client_api.client_api_model import ClientApi
from mapa.manage.api_scope.api_scope_model import ApiScope


class ClientApiScope(BaseModel):
    """ClientApi Modeli"""
    id: UUID
    client_api_id: UUID
    api_scope_id: UUID


class CreateClientApiScope(BaseModel):
    client_api_id: UUID
    api_scope_id: UUID | None = None


class UpdateClientApiScope(BaseModel):
    pass


class UpdateAllClientApiScope(UpdateClientApiScope):
    pass
