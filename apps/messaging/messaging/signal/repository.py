from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from messaging.message.entity import SignalEntity

class SignalRepository(BaseRepository[SignalEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, SignalEntity)
