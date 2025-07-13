from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.connection.connection_model import CreateConnection, UpdateAllConnection, UpdateConnection, Connection
from mapa.spatial.connection.connection_repository import ConnectionRepository


class ConnectionService(BaseEntityService[ConnectionRepository, Connection, CreateConnection, UpdateConnection, UpdateAllConnection]):
    """Connection Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ConnectionRepository, Connection)
