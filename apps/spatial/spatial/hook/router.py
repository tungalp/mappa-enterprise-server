from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.constant import ApiScopeType
from mapa.spatial.hook.hook_model import CreateHook, Hook, UpdateHook
from mapa.spatial.hook.hook_service import HookService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{hook_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_HOOK])
@inject
async def find(
    request: Request,
    hook_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    hook_service: HookService = Depends(
        Provide[AppContainer.hook_package.hook_service])):
    """Hook bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    hook = await hook_service.get(hook_id, tenant_id, field_list)
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return hook


@router.get("/", response_model=PagingResult[Hook])
@authorize([ApiScopeType.QUERY_HOOK])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    hook_service: HookService = Depends(
        Provide[AppContainer.hook_package.hook_service])
):
    tenant_id = request.user.tenant_id
    hooks: PagingResult[Hook] = await hook_service.paging(
        query, tenant_id)  # type: ignore
    return hooks


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_HOOK])
@inject
async def create(
    request: Request,
    items: List[CreateHook] = Body(),
    hook_service: HookService = Depends(
        Provide[AppContainer.hook_package.hook_service])
):
    tenant_id = request.user.tenant_id
    hooks = await hook_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=hooks)
    return result


@router.put("/{hook_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_HOOK])
@inject
async def update(
    request: Request,
    hook_id: str,
    item: UpdateHook = Body(),
    hook_service: HookService = Depends(
        Provide[AppContainer.hook_package.hook_service])
):
    tenant_id = request.user.tenant_id
    hook = await hook_service.update(hook_id, item, tenant_id)
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[hook], affected=1)
    return result


@router.delete("/{hook_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_HOOK])
@inject
async def delete(
    request: Request,
    hook_id: str,
    hook_service: HookService = Depends(
        Provide[AppContainer.hook_package.hook_service])
):
    tenant_id = request.user.tenant_id
    is_success = await hook_service.delete(hook_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_HOOK])
@inject
async def delete_by_ids(
    request: Request,
    hook_ids: List[str],
    hook_service: HookService = Depends(
        Provide[AppContainer.hook_package.hook_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await hook_service.delete_by_ids(hook_ids, tenant_id)
    is_success = True if deleted_count == len(hook_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_HOOK])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    hook_service: HookService = Depends(
        Provide[AppContainer.hook_package.hook_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await hook_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
