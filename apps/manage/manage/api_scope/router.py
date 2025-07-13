from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.api_scope.api_scope_model import CreateApiScope, ApiScope, UpdateApiScope, UpdateAllApiScope
from manage.config.app_container import AppContainer
from mapa.manage.api_scope.api_scope_service import ApiScopeService
from mapa.security import authorize

router = APIRouter()

@router.get("/{api_scope_id}", response_model=ApiScope)
@authorize()
@inject
async def find(
    request: Request,
    api_scope_id: str,
    field_list: List[str | Dict[str, Any]] | None = fields_param(),
    api_scope_service: ApiScopeService = Depends(
        Provide[AppContainer.api_scope_package.api_scope_service])):
    """ApiScope bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    api_scope = await api_scope_service.get(api_scope_id, tenant_id, field_list)
    if not api_scope:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    return api_scope


@router.get("/", response_model=PagingResult[ApiScope])
@authorize()
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    api_scope_service: ApiScopeService = Depends(
        Provide[AppContainer.api_scope_package.api_scope_service])
):
    tenant_id = request.user.tenant_id
    api_scopes: PagingResult[ApiScope] = await api_scope_service.paging(
        query, tenant_id)  # type: ignore
    return api_scopes


@router.post("/", status_code=201, response_model=ActionResult)
@authorize()
@inject
async def create(
    request: Request,
    items: List[CreateApiScope] = Body(),
    api_scope_service: ApiScopeService = Depends(
        Provide[AppContainer.api_scope_package.api_scope_service])
):
    tenant_id = request.user.tenant_id
    api_scopes = await api_scope_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=api_scopes)
    return result


@router.put("/{api_scope_id}", status_code=201, response_model=ActionResult)
@authorize()
@inject
async def update(
    request: Request,
    api_scope_id: str,
    item: UpdateApiScope = Body(),
    api_scope_service: ApiScopeService = Depends(
        Provide[AppContainer.api_scope_package.api_scope_service])
):
    tenant_id = request.user.tenant_id
    api_scope = await api_scope_service.update(api_scope_id, item, tenant_id)
    if not api_scope:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[api_scope], affected=1)
    return result


@router.delete("/{api_scope_id}", status_code=201, response_model=ActionResult)
@authorize()
@inject
async def delete(
    request: Request,
    api_scope_id: str,
    api_scope_service: ApiScopeService = Depends(
        Provide[AppContainer.api_scope_package.api_scope_service])
):
    tenant_id = request.user.tenant_id
    is_success = await api_scope_service.delete(api_scope_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize()
@inject
async def delete_by_ids(
    request: Request,
    api_scope_ids: List[str],
    api_scope_service: ApiScopeService = Depends(
        Provide[AppContainer.api_scope_package.api_scope_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await api_scope_service.delete_by_ids(api_scope_ids, tenant_id)
    is_success = True if deleted_count == len(api_scope_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize()
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    api_scope_service: ApiScopeService = Depends(
        Provide[AppContainer.api_scope_package.api_scope_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await api_scope_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
