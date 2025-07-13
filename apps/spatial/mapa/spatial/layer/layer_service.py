from typing import List
from uuid import UUID

from mapa.core.data.query_args import FilterOp, QueryArgs, Filter
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.result import PagingResult
from mapa.spatial.layer.layer_model import (CreateLayer, Layer, UpdateAllLayer,
                                           UpdateLayer)
from mapa.spatial.layer.layer_repository import LayerRepository
from mapa.spatial.layer_definition.layer_definition_model import \
    CreateLayerDefinition
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService


class LayerService(BaseEntityService[LayerRepository, Layer, CreateLayer, UpdateLayer, UpdateAllLayer]):
    """Layer Servisi"""

    def __init__(self, async_db: AsyncDatabase, layer_definition_service: LayerDefinitionService) -> None:
        self.async_db = async_db
        self.layer_definition_service = layer_definition_service
        super().__init__(async_db, LayerRepository, Layer)

    async def create(self, layer: CreateLayer, tenant_id: str | None = None) -> Layer:
        """Layer oluştururken layer_definition atayarak kaydeder."""

        created_layer = await super().create(layer, tenant_id)
        layer_definition = generate_layer_definition(created_layer.id)
        created_layer_definition = await self.layer_definition_service.create(layer_definition, tenant_id)

        return created_layer

    async def create_all(self, layers: List[CreateLayer], tenant_id: str | None = None) -> List[Layer]:
        """Layer oluştururken layer_definition atayarak kaydeder."""

        created_layers = await super().create_all(layers, tenant_id)
        for created_layer in created_layers:
            layer_definition = generate_layer_definition(created_layer.id)
            created_layer_definition = await self.layer_definition_service.create(layer_definition, tenant_id)

        return created_layers
    
    async def delete_layer_with_rel(self, layer_id: str, tenant_id: str | None = None) -> bool:
        """ Layer bilgisine göre Layer Definition bilgilerini ve Layer bilgilerini siler """
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="layer_id", op=FilterOp.EQUAL, value=layer_id),
        ], limit=0, offset=0)
        layer_definitions = await self.layer_definition_service.paging(query_args, tenant_id)
        for layer_definition in layer_definitions.items:
            await self.layer_definition_service.delete(layer_definition.id, tenant_id)
            
        return await super().delete(layer_id,tenant_id)   

    
    async def delete_layer_by_connection_id_with_rel(self, connection_id: str, tenant_id: str | None = None) -> bool:
        """ Connection bilgisine göre Layer Definition bilgilerini ve Layer bilgilerini siler """
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="connection_id", op=FilterOp.EQUAL, value=connection_id),
        ], limit=0, offset=0)
        
        layers : PagingResult[Layer] = await self.paging(query_args, tenant_id)
        for layer in layers.items:
            await self.delete_layer_with_rel(str(layer.id),tenant_id)
            
        return True

def generate_layer_definition(layer_id: UUID) -> CreateLayerDefinition:
    return CreateLayerDefinition(layer_id=layer_id)
