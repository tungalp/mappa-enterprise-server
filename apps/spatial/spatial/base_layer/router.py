from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.base_layer.base_layer_model import (BaseLayer,
                                                     CreateBaseLayer,
                                                     UpdateBaseLayer)
from mapa.spatial.base_layer.base_layer_service import BaseLayerService
from mapa.spatial.constant import ApiScopeType
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{base_layer_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_BASE_LAYER])
@inject
async def find(
    request: Request,
    base_layer_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    base_layer_service: BaseLayerService = Depends(
        Provide[AppContainer.base_layer_package.base_layer_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    base_layer = await base_layer_service.get(base_layer_id, tenant_id, field_list)
    if not base_layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return base_layer


@router.get("/", response_model=PagingResult[BaseLayer])
@authorize([ApiScopeType.QUERY_BASE_LAYER])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    base_layer_service: BaseLayerService = Depends(
        Provide[AppContainer.base_layer_package.base_layer_service])
):
    tenant_id = request.user.tenant_id
    base_layers: PagingResult[BaseLayer] = await base_layer_service.paging(
        query, tenant_id)  # type: ignore
    return base_layers


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_BASE_LAYER])
@inject
async def create(
    request: Request,
    items: List[CreateBaseLayer] = Body(),
    base_layer_service: BaseLayerService = Depends(
        Provide[AppContainer.base_layer_package.base_layer_service])
):
    tenant_id = request.user.tenant_id
    base_layers = await base_layer_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=base_layers)
    return result


@router.put("/{base_layer_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_BASE_LAYER])
@inject
async def update(
    request: Request,
    base_layer_id: str,
    item: UpdateBaseLayer = Body(),
    base_layer_service: BaseLayerService = Depends(
        Provide[AppContainer.base_layer_package.base_layer_service])
):
    tenant_id = request.user.tenant_id
    base_layer = await base_layer_service.update(base_layer_id, item, tenant_id)
    if not base_layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[base_layer], affected=1)
    return result


@router.delete("/{base_layer_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_BASE_LAYER])
@inject
async def delete(
    request: Request,
    base_layer_id: str,
    base_layer_service: BaseLayerService = Depends(
        Provide[AppContainer.base_layer_package.base_layer_service])
):
    tenant_id = request.user.tenant_id
    is_success = await base_layer_service.delete(base_layer_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_BASE_LAYER])
@inject
async def delete_by_ids(
    request: Request,
    base_layer_ids: List[str],
    base_layer_service: BaseLayerService = Depends(
        Provide[AppContainer.base_layer_package.base_layer_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await base_layer_service.delete_by_ids(base_layer_ids, tenant_id)
    is_success = True if deleted_count == len(base_layer_ids) else False
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_BASE_LAYER])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    base_layer_service: BaseLayerService = Depends(
        Provide[AppContainer.base_layer_package.base_layer_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await base_layer_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
