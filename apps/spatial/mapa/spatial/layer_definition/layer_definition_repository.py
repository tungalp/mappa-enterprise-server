from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.layer_definition.layer_definition_entity import \
    LayerDefinitionEntity


class LayerDefinitionRepository(BaseRepository[LayerDefinitionEntity]):
    """LayerDefinition Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, LayerDefinitionEntity)
