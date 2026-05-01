from typing import Type
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from messaging.room.entity import RoomEntity

class RoomRepository(BaseRepository[RoomEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RoomEntity)
