from ctypes import Array
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.api.api_model import CreateApi, Api, UpdateApi, UpdateAllApi
from manage.config.app_container import AppContainer
from mapa.manage.api.api_service import ApiService
from mapa.core.data.base_entity import Base
from pydantic import BaseModel
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

router = APIRouter()


@router.get("/{api_id}", response_model=Api)
@authorize([ApiScopeType.QUERY_API])
@inject
async def find(
    request: Request,
    api_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    api_service: ApiService = Depends(
        Provide[AppContainer.api_package.api_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    api = await api_service.get(api_id, tenant_id, field_list)
    if not api:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return api


@router.get("/", response_model=PagingResult[Api])
@authorize([ApiScopeType.QUERY_API])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    api_service: ApiService = Depends(
        Provide[AppContainer.api_package.api_service])
):
    tenant_id = request.user.tenant_id
    apis: PagingResult[Api] = await api_service.paging(
        query, tenant_id)  # type: ignore
    return apis


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_API])
@inject
async def create(
    request: Request,
    items: List[CreateApi] = Body(),
    api_service: ApiService = Depends(
        Provide[AppContainer.api_package.api_service])
):
    tenant_id = request.user.tenant_id
    apis = await api_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=apis)
    return result


@router.put("/{api_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_API])
@inject
async def update(
    request: Request,
    api_id: str,
    item: UpdateApi = Body(),
    api_service: ApiService = Depends(
        Provide[AppContainer.api_package.api_service])
):
    tenant_id = request.user.tenant_id
    api = await api_service.update(api_id, item, tenant_id)
    if not api:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[api], affected=1)
    return result


@router.delete("/{api_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_API])
@inject
async def delete(
    request: Request,
    api_id: str,
    api_service: ApiService = Depends(
        Provide[AppContainer.api_package.api_service])
):
    tenant_id = request.user.tenant_id
    is_success = await api_service.delete(api_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.QUERY_API])
@inject
async def delete_by_ids(
    request: Request,
    api_ids: List[str],
    api_service: ApiService = Depends(
        Provide[AppContainer.api_package.api_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await api_service.delete_by_ids(api_ids, tenant_id)
    is_success = True if deleted_count == len(api_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_API])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    api_service: ApiService = Depends(
        Provide[AppContainer.api_package.api_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await api_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
