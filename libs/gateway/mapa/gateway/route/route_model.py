from datetime import datetime
from typing import List, Any, Optional
from uuid import UUID
from pydantic import BaseModel
from mapa.gateway.constant import MethodTypes
from mapa.gateway.integration.integration_model import Integration


class Route(BaseModel):
    """Route Modeli"""

    id: UUID
    path: str
    gateway_api_id: UUID
    method_type: str
    path: str
    created_at: datetime | None = None
    description: str | None = None
    scope: str | None = None
    query: str | None = None
    integration_id: UUID | None = None
    integration: Integration | None = None
    gateway_api: Any | None = None
    cache_timeout: int | None = None  # 60 saniye
    rate_limit: int | None = None  # 1000 adet
    rate_second: int | None = None  # 1000 saniye
    retry_count: int | None = None  # 3 kez
    retry_millisecond: int | None = None  # 500 milisaniye
    full_logging: bool | None = False  # 500 milisaniye


class CreateRoute(BaseModel):
    description: str | None = None
    method_type: str = MethodTypes.GET
    path: str
    scope: str | None = None
    query: str | None = None
    gateway_api_id: UUID
    integration_id: UUID | None = None
    cache_timeout: int | None = None
    rate_limit: int | None = None
    rate_second: int | None = None
    retry_count: int | None = None
    retry_millisecond: int | None = None
    full_logging: bool | None = None


class UpdateRoute(BaseModel):
    description: str | None = None
    method_type: str
    path: str
    scope: str | None = None
    query: str | None = None
    integration_id: UUID | None = None
    cache_timeout: int | None = None
    rate_limit: int | None = None
    rate_second: int | None = None
    retry_count: int | None = None
    retry_millisecond: int | None = None
    full_logging: bool | None = None


class UpdateAllRoute(BaseModel):
    method_type: str
    description: str | None = None
    integration_id: UUID | None = None
    scope: str | None = None
    cache_timeout: int | None = None
    rate_limit: int | None = None
    rate_second: int | None = None
    retry_count: int | None = None
    retry_millisecond: int | None = None
    full_logging: bool | None = None
