from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID
from pydantic import BaseModel
from mapa.gateway.constant import ApiTypes
from mapa.gateway.integration.integration_model import Integration
from mapa.gateway.route.route_model import Route


class GatewayApi(BaseModel):
    """Api Modeli"""
    id: UUID
    name: str
    type: str
    path: str
    created_at: datetime | None = None
    description: str | None = None
    integrations: List[Integration] | None = None
    routes: List[Route] | None = None
    identifier: str
    manage_api_id: UUID | None = None
    context: Dict[str, Any] | None = None


class CreateGatewayApi(BaseModel):
    name: str
    path: str
    description: str | None = None
    type: str = ApiTypes.HTTP
    identifier: str
    manage_api_id: UUID | None = None
    context: Dict[str, Any] | None = None


class UpdateGatewayApi(BaseModel):
    name: str
    description: str | None = None
    path: str
    identifier: str
    context: Dict[str, Any] | None = None


class UpdateAllGatewayApi(BaseModel):
    description: str | None = None
    context: Dict[str, Any] | None = None
    
class ExportGatewayApi(GatewayApi):
    """ExportGatewayApi Modeli"""
  
    scopes: List[Any]
