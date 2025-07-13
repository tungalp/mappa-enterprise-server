from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.layer.layer_entity import LayerEntity


class LayerRepository(BaseRepository[LayerEntity]):
    """Layer Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, LayerEntity)
