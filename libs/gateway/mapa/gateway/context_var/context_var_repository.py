from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.gateway.context_var.context_var_entity import ContextVarEntity


class ContextVarRepository(BaseRepository[ContextVarEntity]):
    """ContextVar Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ContextVarEntity)
