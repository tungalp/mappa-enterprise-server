from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from mapa.spatial.bookmark.bookmark_model import Bookmark
from mapa.spatial.constant import MapWidgetType, SridTypes
from mapa.spatial.map_base_layer.map_base_layer_model import MapBaseLayer
from mapa.spatial.map_layer.map_layer_model import MapLayer
from mapa.spatial.models.merge_layer_model import MergeLayer
from mapa.spatial.namespace.namespace_model import Namespace
from mapa.spatial.reference.reference_model import Reference
from pydantic import BaseModel


# widget_types json parametresi type model
class Types(BaseModel):
    """Types Modeli"""
    key: MapWidgetType

# map_layers - references - bookmarks - map_base_layers propları map serviste ki get_map_full_info methodu
# kullanılarak sorgu işlemi yapıldı zaman doldurulmaktadır.
class Map(BaseModel):
    """Map Modeli"""
    id: UUID
    name: str
    description: str | None = None
    title: str | None = None
    initial_extent: str
    full_extent: str
    zoom: int | None = None
    namespace_id: UUID | None = None
    namespace: Namespace | None = None
    widget_types: List[Types] | None = None
    srid: SridTypes
    

    references: List[Reference] | None = None
    bookmarks: List[Bookmark] | None = None
    # map_layers: Optional[List['MapLayer']] | None = None
    # map_base_layers: Optional[List['MapBaseLayer']] | None = None
    map_layers: List[MapLayer] | None = None
    map_base_layers: List[MapBaseLayer] | None = None
    merge_layers: List[MergeLayer] | None = None


class CreateMap(BaseModel):
    """CreateMap Modeli"""
    name: str
    description: str | None = None
    title: str | None = None
    initial_extent: str
    full_extent: str
    zoom: int | None = None
    namespace_id: UUID | None = None
    widget_types: List[Types] | None = None
    srid: SridTypes


class UpdateMap(BaseModel):
    """UpdateMap Modeli"""
    name: str
    description: str | None = None
    title: str | None = None
    initial_extent: str
    full_extent: str
    zoom: int | None = None
    namespace_id: UUID | None = None
    widget_types: List[Types] | None = None
    srid: SridTypes


class UpdateAllMap(BaseModel):
    """UpdateAllMap Modeli"""
    description: str | None = None
    title: str | None = None
    zoom: int | None = None
    widget_types: List[Types] | None = None


#  Model import edilirken circular dep. hatasını gidermek için tanımlanmıştır.
#  ve bundan dolayı da maplayer - mapbaselayer property'si Optional keyword'u ile tanımlanmıştır
# from mapa.spatial.map_base_layer.map_base_layer_model import MapBaseLayer
# from mapa.spatial.map_layer.map_layer_model import MapLayer
# Map.model_rebuild()
