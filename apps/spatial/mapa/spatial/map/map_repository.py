from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.map.map_entity import MapEntity


class MapRepository(BaseRepository[MapEntity]):
    """Map Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, MapEntity)
