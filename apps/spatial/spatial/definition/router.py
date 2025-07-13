from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.constant import ApiScopeType
from mapa.spatial.definition.definition_model import (CreateDefinition,
                                                     Definition,
                                                     UpdateDefinition)
from mapa.spatial.definition.definition_service import DefinitionService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from mapa.spatial.layer_hook.layer_hook_model import CreateLayerHook, UpdateLayerHook
from spatial.config.app_container import AppContainer
import json
router = APIRouter()


@router.get("/{definition_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_DEFINITION])
@inject
async def find(
    request: Request,
    definition_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    definition = await definition_service.get(definition_id, tenant_id, field_list)
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return definition


@router.get("/", response_model=PagingResult[Definition])
@authorize([ApiScopeType.QUERY_DEFINITION])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])
):
    tenant_id = request.user.tenant_id
    definitions: PagingResult[Definition] = await definition_service.paging(
        query, tenant_id)  # type: ignore
    return definitions


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_DEFINITION])
@inject
async def create(
    request: Request,
    items: List[CreateDefinition] = Body(),
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])
):
    tenant_id = request.user.tenant_id
    definitions = await definition_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=definitions)
    return result


@router.put("/{definition_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_DEFINITION])
@inject
async def update(
    request: Request,
    definition_id: str,
    item: UpdateDefinition = Body(),
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])
):
    tenant_id = request.user.tenant_id
    definition = await definition_service.update(definition_id, item, tenant_id)
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[definition], affected=1)
    return result


@router.delete("/{definition_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_DEFINITION])
@inject
async def delete(
    request: Request,
    definition_id: str,
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])
):
    tenant_id = request.user.tenant_id
    is_success = await definition_service.delete(definition_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_DEFINITION])
@inject
async def delete_by_ids(
    request: Request,
    definition_ids: List[str],
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await definition_service.delete_by_ids(definition_ids, tenant_id)
    is_success = True if deleted_count == len(definition_ids) else False
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_DEFINITION])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await definition_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/delete_definition_with_rel/{definition_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_DEFINITION])
@inject
async def delete_definition_with_rel(
    request: Request,
    definition_id: str,
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])
):
    tenant_id = request.user.tenant_id
    is_success = await definition_service.delete_definition_with_rel(definition_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/update_definition_with_rel/{definition_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_DEFINITION])
@inject
async def update_definition_with_rel(
    request: Request,
    definition_id: str,
    item: Any = Body(),
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])
):
    tenant_id = request.user.tenant_id
    update_entity = UpdateDefinition(**(item['update_entity']))
    
    layer_hooks = (item['layer_hooks']) if len((item['layer_hooks'])) > 0 else []
    layer_hooks_entity = []
    if isinstance(layer_hooks, list) and len(layer_hooks) > 0:
        for hook in layer_hooks:
            layer_hooks_entity.append(UpdateLayerHook(**hook))
    
    definition = await definition_service.update_definition_with_rel(definition_id, update_entity, layer_hooks_entity, tenant_id)
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[definition], affected=1)
    return result


@router.post("/create_definition_with_rel/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_DEFINITION])
@inject
async def create_definition_with_rel(
    request: Request,
    item: Any = Body(),
    definition_service: DefinitionService = Depends(
        Provide[AppContainer.definition_package.definition_service])
):
    tenant_id = request.user.tenant_id
    
    definitions = (item['definitionData']) if len((item['definitionData'])) > 0 else []
    definitions_entity = []
    if isinstance(definitions, list) and len(definitions) > 0:
        for definition in definitions:
            definitions_entity.append(CreateDefinition(**definition))
            
    selected_layer_id = item['selectedLayerId']       
    
    layer_hooks = (item['layerHooksData']) if len((item['layerHooksData'])) > 0 else []
    layer_hooks_entity = []
    if isinstance(layer_hooks, list) and len(layer_hooks) > 0:
        for hook in layer_hooks:
            layer_hooks_entity.append(CreateLayerHook(**hook))
            
    response_dict = await definition_service.create_definition_with_rel(definitions_entity, selected_layer_id, layer_hooks_entity, tenant_id)
    created_definitions = None
    created_layer_definition_id = None
    
    if response_dict is not None:
        created_definitions = response_dict["created_definitions"]
        created_layer_definition_id = response_dict["created_layer_definition_id"]
    
    if created_definitions is None or created_layer_definition_id is None:
        result = ActionResult(success=False, items=[])
        
    result = ActionResult(success=True, items=definitions,message=created_layer_definition_id)
    return result
