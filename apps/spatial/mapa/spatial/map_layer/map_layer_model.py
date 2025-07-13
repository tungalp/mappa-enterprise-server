from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from mapa.spatial.layer_definition.layer_definition_model import LayerDefinition
from pydantic import BaseModel

#  Model import edilirken circular dep. hatasını gidermek için tanımlanmıştır.
if TYPE_CHECKING:
    from mapa.spatial.map.map_model import Map


class Params(BaseModel):
    """Params Modeli"""
    visible: bool | None = None
    opacity: float | None = None


class MapLayer(BaseModel):
    """MapLayer Modeli"""
    id: UUID
    name: str
    parent_id: str | None = None
    params: Params | None = None
    order: int
    map_id: UUID
    map: Optional['Map'] | None = None
    layer_definition_id: UUID | None = None
    layer_definition: LayerDefinition | None = None


class CreateMapLayer(BaseModel):
    """CreateMapLayer Modeli"""
    name: str
    parent_id: str | None = None
    params: Params | None = None
    order: int
    map_id: UUID
    layer_definition_id: UUID | None = None


class UpdateMapLayer(BaseModel):
    """UpdateMapLayer Modeli"""
    name: str
    parent_id: str | None = None
    params: Params | None = None
    order: int
    map_id: UUID
    layer_definition_id: UUID | None = None


class UpdateAllMapLayer(BaseModel):
    """UpdateAllMapLayer Modeli"""
    parent_id: str | None = None
    params: Any | None = None


#  Model import edilirken circular dep. hatasını gidermek için tanımlanmıştır.
#  ve bundan dolayı da map property'si Optional keyword'u ile tanımlanmıştır
# from mapa.spatial.map.map_model import Map
# MapLayer.model_rebuild()
