from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.reference.reference_entity import ReferenceEntity


class ReferenceRepository(BaseRepository[ReferenceEntity]):
    """Reference Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ReferenceEntity)
