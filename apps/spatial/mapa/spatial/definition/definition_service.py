from typing import Any, List, Dict
from uuid import UUID
import uuid
from mapa.core.data.query_args import FilterOp, QueryArgs, Filter
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.definition.definition_model import (CreateDefinition,
                                                     Definition,
                                                     UpdateAllDefinition,
                                                     UpdateDefinition)
from mapa.spatial.definition.definition_repository import DefinitionRepository

from mapa.spatial.layer_definition.layer_definition_model import CreateLayerDefinition, LayerDefinition
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService
from mapa.spatial.layer_hook.layer_hook_model import CreateLayerHook, UpdateLayerHook
from mapa.spatial.layer_hook.layer_hook_service import LayerHookService

class DefinitionService(BaseEntityService[DefinitionRepository, Definition, CreateDefinition, UpdateDefinition, UpdateAllDefinition]):
    """Definition Servisi"""

    def __init__(self, async_db: AsyncDatabase,layer_definition_service: LayerDefinitionService,layer_hook_service: LayerHookService ) -> None:
        self.async_db = async_db
        self.layer_definition_service = layer_definition_service
        self.layer_hook_service = layer_hook_service
        super().__init__(async_db, DefinitionRepository, Definition)
    

    async def delete_definition_with_rel(self, definition_id: str, tenant_id: str | None = None) -> bool:
        """ Definition bilgisine göre Layer Definition bilgilerini ve Definition bilgilerini siler """
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="definition_id", op=FilterOp.EQUAL, value=definition_id),
        ], limit=0, offset=0)
        
        layer_definitions = await self.layer_definition_service.paging(query_args, tenant_id)
        
        for layer_definition in layer_definitions.items:
            
            layer_hooks_query_args: QueryArgs = QueryArgs(where=[
            Filter(field="layer_definition_id", op=FilterOp.EQUAL, value=layer_definition.id),
            ], limit=0, offset=0)
            
            rst_layer_hook = await self.layer_hook_service.delete_all(layer_hooks_query_args, tenant_id)
            await self.layer_definition_service.delete(layer_definition.id, tenant_id)
            
        return await super().delete(definition_id,tenant_id)   
    
    
    async def update_definition_with_rel(self, obj_id: Any, input_definition: UpdateDefinition,input_layer_hooks: List[UpdateLayerHook], tenant_id: str | None = None) -> Definition | None:

        inserted_layer_hooks = []
        try:
            if len(input_layer_hooks) > 0:
                layer_definition_id = input_layer_hooks[0].layer_definition_id
                query_args: QueryArgs = QueryArgs(where=[
                Filter(field="layer_definition_id", op=FilterOp.EQUAL, value=layer_definition_id),
                ], limit=0, offset=0)

                inserts = await self.layer_hook_service.find(query_args, tenant_id)
                for insert in inserts:
                    inserted_layer_hooks.append(CreateLayerHook( route_id= insert.route_id,
                        layer_definition_id= insert.layer_definition_id,
                        widget_name= insert.widget_name,
                        hook_operation_type= insert.hook_operation_type))
                
                rst = await self.layer_hook_service.delete_all(query_args, tenant_id)
                create_layer_hooks = []
                for layer_hook in input_layer_hooks:
                    create_layer_hooks.append(CreateLayerHook(
                        route_id= layer_hook.route_id,
                        layer_definition_id= layer_hook.layer_definition_id,
                        widget_name= layer_hook.widget_name,
                        hook_operation_type= layer_hook.hook_operation_type,
                    ))
                rst = await self.layer_hook_service.create_all(create_layer_hooks, tenant_id)
            else:
                query_args: QueryArgs = QueryArgs(where=[
                Filter(field="definition_id", op=FilterOp.EQUAL, value=obj_id),
                ], limit=0, offset=0)
                
                layer_definitions = await self.layer_definition_service.find(query_args, tenant_id)
                
                for layer_definition in layer_definitions:
                    query_args: QueryArgs = QueryArgs(where=[
                    Filter(field="layer_definition_id", op=FilterOp.EQUAL, value=layer_definition.id),
                    ], limit=0, offset=0)

                    rst = await self.layer_hook_service.delete_all(query_args, tenant_id)
                    
        except Exception as Ex:
            if inserted_layer_hooks is not None and len(inserted_layer_hooks)>0:
                await self.layer_hook_service.create_all(inserted_layer_hooks, tenant_id)   
            
            raise Ex
        
        return await super().update(obj_id,input_definition,tenant_id)   
    
    
    async def create_definition_with_rel(self, create_definitions: List[CreateDefinition], selectedLayerId: Any, create_layer_hooks: List[CreateLayerHook], tenant_id: str | None = None) -> Dict[str, Any] | None:

        created_definitions_id_list = []
        created_layer_definition_id_list = []
        created_layer_hooks_list = []
        created_definitions = None
        created_layer_definition_id = None
        try:
            # Definition insert edilir...
            created_definitions = await super().create_all(create_definitions, tenant_id)
            
            for created_definition in created_definitions:
                created_definitions_id_list.append(created_definition.id)
                
                # Layer Definition insert edilir...
                layerDefinitionData = CreateLayerDefinition (layer_id= selectedLayerId, definition_id= created_definition.id)
                created_layer_definition = await self.layer_definition_service.create(layerDefinitionData, tenant_id)
                created_layer_definition_id_list.append(created_layer_definition.id)
                created_layer_definition_id = created_layer_definition.id
                
                if created_layer_definition is not None and len(create_layer_hooks) > 0:
                    for item in create_layer_hooks:
                        item.layer_definition_id = created_layer_definition.id
                    # Layer Hooks insert edilir... 
                    created_layer_hooks = await self.layer_hook_service.create_all(create_layer_hooks, tenant_id)
                    for created_layer_hook in created_layer_hooks:
                        created_layer_hooks_list.append(created_layer_hook.id)
        except Exception as Ex:
            
            if created_layer_hooks_list is not None and len(created_layer_hooks_list)>0:
                await self.layer_hook_service.delete_by_ids(created_layer_hooks_list, tenant_id)   
                
            if created_layer_definition_id_list is not None and len(created_layer_definition_id_list)>0:
                await self.layer_definition_service.delete_by_ids(created_layer_definition_id_list, tenant_id)  
                
            if created_definitions_id_list is not None and len(created_definitions_id_list)>0:
                await super().delete_by_ids(created_definitions_id_list, tenant_id)  
               
            raise Ex
        
        return {
            "created_definitions": created_definitions,
            "created_layer_definition_id": str(created_layer_definition_id)
        }
      