from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.layer_hook.layer_hook_entity import LayerHookEntity


class LayerHookRepository(BaseRepository[LayerHookEntity]):
    """LayerHook Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, LayerHookEntity)
