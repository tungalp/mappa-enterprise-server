from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.layer_definition.layer_definition_model import (
    CreateLayerDefinition, LayerDefinition, UpdateAllLayerDefinition,
    UpdateLayerDefinition)
from mapa.spatial.layer_definition.layer_definition_repository import \
    LayerDefinitionRepository

class LayerDefinitionService(BaseEntityService[LayerDefinitionRepository, LayerDefinition, CreateLayerDefinition, UpdateLayerDefinition, UpdateAllLayerDefinition]):
    """LayerDefinition Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        self.async_db = async_db
        super().__init__(async_db, LayerDefinitionRepository, LayerDefinition)


