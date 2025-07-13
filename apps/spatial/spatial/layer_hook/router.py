from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.constant import ApiScopeType
from mapa.spatial.layer_hook.layer_hook_model import (CreateLayerHook,
                                                     LayerHook,
                                                     UpdateLayerHook)
from mapa.spatial.layer_hook.layer_hook_service import LayerHookService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{layer_hook_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_LAYER_HOOK])
@inject
async def find(
    request: Request,
    layer_hook_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    layer_hook_service: LayerHookService = Depends(
        Provide[AppContainer.layer_hook_package.layer_hook_service])):
    """LayerHook bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    layer_hook = await layer_hook_service.get(layer_hook_id, tenant_id, field_list)
    if not layer_hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return layer_hook


@router.get("/", response_model=PagingResult[LayerHook])
@authorize([ApiScopeType.QUERY_LAYER_HOOK])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    layer_hook_service: LayerHookService = Depends(
        Provide[AppContainer.layer_hook_package.layer_hook_service])
):
    tenant_id = request.user.tenant_id
    layer_hooks: PagingResult[LayerHook] = await layer_hook_service.paging(
        query, tenant_id)  # type: ignore
    return layer_hooks


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_HOOK])
@inject
async def create(
    request: Request,
    items: List[CreateLayerHook] = Body(),
    layer_hook_service: LayerHookService = Depends(
        Provide[AppContainer.layer_hook_package.layer_hook_service])
):
    tenant_id = request.user.tenant_id
    layer_hooks = await layer_hook_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=layer_hooks)
    return result


@router.put("/{layer_hook_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_HOOK])
@inject
async def update(
    request: Request,
    layer_hook_id: str,
    item: UpdateLayerHook = Body(),
    layer_hook_service: LayerHookService = Depends(
        Provide[AppContainer.layer_hook_package.layer_hook_service])
):
    tenant_id = request.user.tenant_id
    layer_hook = await layer_hook_service.update(layer_hook_id, item, tenant_id)
    if not layer_hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[layer_hook], affected=1)
    return result


@router.delete("/{layer_hook_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_HOOK])
@inject
async def delete(
    request: Request,
    layer_hook_id: str,
    layer_hook_service: LayerHookService = Depends(
        Provide[AppContainer.layer_hook_package.layer_hook_service])
):
    tenant_id = request.user.tenant_id
    is_success = await layer_hook_service.delete(layer_hook_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_HOOK])
@inject
async def delete_by_ids(
    request: Request,
    layer_hook_ids: List[str],
    layer_hook_service: LayerHookService = Depends(
        Provide[AppContainer.layer_hook_package.layer_hook_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await layer_hook_service.delete_by_ids(layer_hook_ids, tenant_id)
    is_success = True if deleted_count == len(layer_hook_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_LAYER_HOOK])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    layer_hook_service: LayerHookService = Depends(
        Provide[AppContainer.layer_hook_package.layer_hook_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await layer_hook_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
