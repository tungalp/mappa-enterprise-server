from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.hook.hook_entity import HookEntity


class HookRepository(BaseRepository[HookEntity]):
    """Hook Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, HookEntity)
