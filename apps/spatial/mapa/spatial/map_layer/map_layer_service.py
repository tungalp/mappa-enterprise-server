from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.map_layer.map_layer_model import (CreateMapLayer, MapLayer,
                                                   UpdateAllMapLayer,
                                                   UpdateMapLayer)
from mapa.spatial.map_layer.map_layer_repository import MapLayerRepository


class MapLayerService(BaseEntityService[MapLayerRepository, MapLayer, CreateMapLayer, UpdateMapLayer, UpdateAllMapLayer]):
    """MapLayer Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, MapLayerRepository, MapLayer)
