from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.constant import ApiScopeType
from mapa.spatial.layer_definition.layer_definition_model import (
    CreateLayerDefinition, LayerDefinition, UpdateLayerDefinition)
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{layer_definition_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_LAYER_DEFINITION])
@inject
async def find(
    request: Request,
    layer_definition_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    layer_definition_service: LayerDefinitionService = Depends(
        Provide[AppContainer.layer_definition_package.layer_definition_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    layer_definition = await layer_definition_service.get(layer_definition_id, tenant_id, field_list)
    if not layer_definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return layer_definition


@router.get("/", response_model=PagingResult[LayerDefinition])
@authorize([ApiScopeType.QUERY_LAYER_DEFINITION])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    layer_definition_service: LayerDefinitionService = Depends(
        Provide[AppContainer.layer_definition_package.layer_definition_service])
):
    tenant_id = request.user.tenant_id
    layer_definitions: PagingResult[LayerDefinition] = await layer_definition_service.paging(
        query, tenant_id)  # type: ignore
    return layer_definitions


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_DEFINITION])
@inject
async def create(
    request: Request,
    items: List[CreateLayerDefinition] = Body(),
    layer_definition_service: LayerDefinitionService = Depends(
        Provide[AppContainer.layer_definition_package.layer_definition_service])
):
    tenant_id = request.user.tenant_id
    layer_definitions = await layer_definition_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=layer_definitions)
    return result


@router.put("/{layer_definition_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_DEFINITION])
@inject
async def update(
    request: Request,
    layer_definition_id: str,
    item: UpdateLayerDefinition = Body(),
    layer_definition_service: LayerDefinitionService = Depends(
        Provide[AppContainer.layer_definition_package.layer_definition_service])
):
    tenant_id = request.user.tenant_id
    layer_definition = await layer_definition_service.update(layer_definition_id, item, tenant_id)
    if not layer_definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[layer_definition], affected=1)
    return result


@router.delete("/{layer_definition_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_DEFINITION])
@inject
async def delete(
    request: Request,
    layer_definition_id: str,
    layer_definition_service: LayerDefinitionService = Depends(
        Provide[AppContainer.layer_definition_package.layer_definition_service])
):
    tenant_id = request.user.tenant_id
    is_success = await layer_definition_service.delete(layer_definition_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_DEFINITION])
@inject
async def delete_by_ids(
    request: Request,
    layer_definition_ids: List[str],
    layer_definition_service: LayerDefinitionService = Depends(
        Provide[AppContainer.layer_definition_package.layer_definition_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await layer_definition_service.delete_by_ids(layer_definition_ids, tenant_id)
    is_success = True if deleted_count == len(layer_definition_ids) else False
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_DEFINITION])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    layer_definition_service: LayerDefinitionService = Depends(
        Provide[AppContainer.layer_definition_package.layer_definition_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await layer_definition_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())

