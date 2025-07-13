from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.outbox.outbox_entity import OutboxEntity


class OutboxRepository(BaseRepository[OutboxEntity]):
    """Outbox Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OutboxEntity)
