from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.constant import ApiScopeType
from mapa.spatial.map_layer.map_layer_model import (CreateMapLayer, MapLayer,
                                                   UpdateMapLayer)
from mapa.spatial.map_layer.map_layer_service import MapLayerService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{map_layer_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_MAP_LAYER])
@inject
async def find(
    request: Request,
    map_layer_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    map_layer_service: MapLayerService = Depends(
        Provide[AppContainer.map_layer_package.map_layer_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    map_layer = await map_layer_service.get(map_layer_id, tenant_id, field_list)
    if not map_layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return map_layer


@router.get("/", response_model=PagingResult[MapLayer])
@authorize([ApiScopeType.QUERY_MAP_LAYER])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    map_layer_service: MapLayerService = Depends(
        Provide[AppContainer.map_layer_package.map_layer_service])
):
    tenant_id = request.user.tenant_id
    map_layers: PagingResult[MapLayer] = await map_layer_service.paging(
        query, tenant_id)  # type: ignore
    return map_layers


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP_LAYER])
@inject
async def create(
    request: Request,
    items: List[CreateMapLayer] = Body(),
    map_layer_service: MapLayerService = Depends(
        Provide[AppContainer.map_layer_package.map_layer_service])
):
    tenant_id = request.user.tenant_id
    map_layers = await map_layer_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=map_layers)
    return result


@router.put("/{map_layer_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP_LAYER])
@inject
async def update(
    request: Request,
    map_layer_id: str,
    item: UpdateMapLayer = Body(),
    map_layer_service: MapLayerService = Depends(
        Provide[AppContainer.map_layer_package.map_layer_service])
):
    tenant_id = request.user.tenant_id
    map_layer = await map_layer_service.update(map_layer_id, item, tenant_id)
    if not map_layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[map_layer], affected=1)
    return result


@router.delete("/{map_layer_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP_LAYER])
@inject
async def delete(
    request: Request,
    map_layer_id: str,
    map_layer_service: MapLayerService = Depends(
        Provide[AppContainer.map_layer_package.map_layer_service])
):
    tenant_id = request.user.tenant_id
    is_success = await map_layer_service.delete(map_layer_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP_LAYER])
@inject
async def delete_by_ids(
    request: Request,
    map_layer_ids: List[str],
    map_layer_service: MapLayerService = Depends(
        Provide[AppContainer.map_layer_package.map_layer_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await map_layer_service.delete_by_ids(map_layer_ids, tenant_id)
    is_success = True if deleted_count == len(map_layer_ids) else False
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP_LAYER])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    map_layer_service: MapLayerService = Depends(
        Provide[AppContainer.map_layer_package.map_layer_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await map_layer_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
