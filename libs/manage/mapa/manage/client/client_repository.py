from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.client.client_entity import ClientEntity


class ClientRepository(BaseRepository[ClientEntity]):
    """Client Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ClientEntity)
