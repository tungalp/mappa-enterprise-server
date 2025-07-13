from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.namespace.namespace_entity import NamespaceEntity


class NamespaceRepository(BaseRepository[NamespaceEntity]):
    """Namespace Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, NamespaceEntity)
