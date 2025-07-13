from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.constant import ApiScopeType
from mapa.spatial.layer.layer_model import CreateLayer, Layer, UpdateLayer
from mapa.spatial.layer.layer_service import LayerService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{layer_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_LAYER])
@inject
async def find(
    request: Request,
    layer_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    layer = await layer_service.get(layer_id, tenant_id, field_list)
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return layer


@router.get("/", response_model=PagingResult[Layer])
@authorize([ApiScopeType.QUERY_LAYER])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])
):
    tenant_id = request.user.tenant_id
    layers: PagingResult[Layer] = await layer_service.paging(
        query, tenant_id)  # type: ignore
    return layers


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER])
@inject
async def create(
    request: Request,
    items: List[CreateLayer] = Body(),
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])
):
    tenant_id = request.user.tenant_id
    layers = await layer_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=layers)
    return result


@router.put("/{layer_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER])
@inject
async def update(
    request: Request,
    layer_id: str,
    item: UpdateLayer = Body(),
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])
):
    tenant_id = request.user.tenant_id
    layer = await layer_service.update(layer_id, item, tenant_id)
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[layer], affected=1)
    return result


@router.delete("/{layer_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER])
@inject
async def delete(
    request: Request,
    layer_id: str,
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])
):
    tenant_id = request.user.tenant_id
    is_success = await layer_service.delete(layer_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER])
@inject
async def delete_by_ids(
    request: Request,
    layer_ids: List[str],
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await layer_service.delete_by_ids(layer_ids, tenant_id)
    is_success = True if deleted_count == len(layer_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await layer_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.put("/updateAll/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER])
@inject
async def updateAll(
    request: Request,
    items: List[Layer] = Body(),
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])
):
    tenant_id = request.user.tenant_id
    for item in items:
        layer = await layer_service.update(item.id, item, tenant_id) # type: ignore
        if not layer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    result = ActionResult(success=True, items=items, affected=len(items))
    return result


@router.delete("/delete_layer_with_rel/{layer_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER])
@inject
async def delete_layer_with_rel(
    request: Request,
    layer_id: str,
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])
):
    tenant_id = request.user.tenant_id
    is_success = await layer_service.delete_layer_with_rel(layer_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.delete("/delete_layer_by_connection_id_with_rel/{connection_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER])
@inject
async def delete_layer_by_connection_id_with_rel(
    request: Request,
    connection_id: str,
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service])
):
    tenant_id = request.user.tenant_id
    is_success = await layer_service.delete_layer_by_connection_id_with_rel(connection_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())
