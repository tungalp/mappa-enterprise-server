from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.map_base_layer.map_base_layer_model import (
    CreateMapBaseLayer, MapBaseLayer, UpdateAllMapBaseLayer,
    UpdateMapBaseLayer)
from mapa.spatial.map_base_layer.map_base_layer_repository import \
    MapBaseLayerRepository


class MapBaseLayerService(BaseEntityService[MapBaseLayerRepository, MapBaseLayer, CreateMapBaseLayer, UpdateMapBaseLayer, UpdateAllMapBaseLayer]):
    """MapBaseLayer Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, MapBaseLayerRepository, MapBaseLayer)
