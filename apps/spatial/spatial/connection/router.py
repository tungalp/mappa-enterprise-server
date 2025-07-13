from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.connection.connection_model import (Connection,
                                                     CreateConnection,
                                                     UpdateConnection)
from mapa.spatial.connection.connection_service import ConnectionService
from mapa.spatial.constant import ApiScopeType
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/{connection_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_CONNECTION])
@inject
async def find(
    request: Request,
    connection_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    connection_service: ConnectionService = Depends(
        Provide[AppContainer.connection_package.connection_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    connection = await connection_service.get(connection_id, tenant_id, field_list)
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return connection


@router.get("/", response_model=PagingResult[Connection])
@authorize([ApiScopeType.QUERY_CONNECTION])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    connection_service: ConnectionService = Depends(
        Provide[AppContainer.connection_package.connection_service])
):
    tenant_id = request.user.tenant_id
    connections: PagingResult[Connection] = await connection_service.paging(
        query, tenant_id)  # type: ignore
    return connections


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION])
@inject
async def create(
    request: Request,
    items: List[CreateConnection] = Body(),
    connection_service: ConnectionService = Depends(
        Provide[AppContainer.connection_package.connection_service])
):
    tenant_id = request.user.tenant_id
    connections = await connection_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=connections)
    return result


@router.put("/{connection_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION])
@inject
async def update(
    request: Request,
    connection_id: str,
    item: UpdateConnection = Body(),
    connection_service: ConnectionService = Depends(
        Provide[AppContainer.connection_package.connection_service])
):
    tenant_id = request.user.tenant_id
    connection = await connection_service.update(connection_id, item, tenant_id)
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[connection], affected=1)
    return result


@router.delete("/{connection_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION])
@inject
async def delete(
    request: Request,
    connection_id: str,
    connection_service: ConnectionService = Depends(
        Provide[AppContainer.connection_package.connection_service])
):
    tenant_id = request.user.tenant_id
    is_success = await connection_service.delete(connection_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION])
@inject
async def delete_by_ids(
    request: Request,
    connection_ids: List[str],
    connection_service: ConnectionService = Depends(
        Provide[AppContainer.connection_package.connection_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await connection_service.delete_by_ids(connection_ids, tenant_id)
    is_success = True if deleted_count == len(connection_ids) else False
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    connection_service: ConnectionService = Depends(
        Provide[AppContainer.connection_package.connection_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await connection_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
