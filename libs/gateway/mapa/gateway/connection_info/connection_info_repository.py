from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.gateway.connection_info.connection_info_entity import ConnectionInfoEntity

class ConnectionInfoRepository(BaseRepository[ConnectionInfoEntity]):
    """ConnectionInfo Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ConnectionInfoEntity)
