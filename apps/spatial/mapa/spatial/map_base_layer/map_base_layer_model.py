from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from mapa.spatial.base_layer.base_layer_model import BaseLayer
from pydantic import BaseModel

#  Model import edilirken circular dep. hatasını gidermek için tanımlanmıştır.
if TYPE_CHECKING:
    from mapa.spatial.map.map_model import Map
    
    
class MapBaseLayer(BaseModel):
    """MapBaseLayer Modeli"""
    
    id: UUID
    order: int
    map_id: UUID
    base_layer_id: UUID

    base_layer: BaseLayer | None = None
    map: Optional[Map] | None = None


class CreateMapBaseLayer(BaseModel):
    """CreateMapBaseLayer Modeli"""
    order: int
    map_id: UUID
    base_layer_id: UUID


class UpdateMapBaseLayer(BaseModel):
    """UpdateMapBaseLayer Modeli"""
    order: int
    map_id: UUID
    base_layer_id: UUID


class UpdateAllMapBaseLayer(BaseModel):
    """UpdateAllMapBaseLayer Modeli"""
    order: int
    map_id: UUID
    base_layer_id: UUID


#  Model import edilirken circular dep. hatasını gidermek için tanımlanmıştır.
#  ve bundan dolayı da map property'si Optional keyword'u ile tanımlanmıştır
# from mapa.spatial.map.map_model import Map
# MapBaseLayer.model_rebuild()
