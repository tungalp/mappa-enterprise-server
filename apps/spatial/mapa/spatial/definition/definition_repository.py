from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.definition.definition_entity import DefinitionEntity


class DefinitionRepository(BaseRepository[DefinitionEntity]):
    """Definition Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, DefinitionEntity)
