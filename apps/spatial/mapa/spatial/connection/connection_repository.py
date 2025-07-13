from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.connection.connection_entity import ConnectionEntity


class ConnectionRepository(BaseRepository[ConnectionEntity]):
    """Connection Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ConnectionEntity)
