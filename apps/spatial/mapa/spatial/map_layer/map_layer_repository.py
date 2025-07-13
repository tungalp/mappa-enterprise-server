from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.map_layer.map_layer_entity import MapLayerEntity


class MapLayerRepository(BaseRepository[MapLayerEntity]):
    """MapLayer Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, MapLayerEntity)
