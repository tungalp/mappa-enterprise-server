from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.map_base_layer.map_base_layer_entity import MapBaseLayerEntity


class MapBaseLayerRepository(BaseRepository[MapBaseLayerEntity]):
    """MapBaseLayer Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, MapBaseLayerEntity)
