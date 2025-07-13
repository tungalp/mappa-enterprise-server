from ctypes import Array
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID,uuid4
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.gateway.constant import ApiScopeType
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo, CreateConnectionInfo, UpdateConnectionInfo
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService
from gateway.config.app_container import AppContainer
from mapa.core.data.base_entity import Base
from pydantic import BaseModel
from mapa.security import authorize

router = APIRouter()

@router.get("/{connection_info_id}", response_model=ConnectionInfo)
@authorize([ApiScopeType.QUERY_CONNECTION_INFO])
@inject
async def find(
    request: Request,
    connection_info_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    connection_info_service: ConnectionInfoService = Depends(
        Provide[AppContainer.connection_info_package.connection_info_service])):
    """ConnectionInfo bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    connection_info = await connection_info_service.get(connection_info_id, tenant_id, field_list, True)
    if not connection_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return connection_info


@router.get("/", response_model=PagingResult[ConnectionInfo])
@authorize([ApiScopeType.QUERY_CONNECTION_INFO])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    connection_info_service: ConnectionInfoService = Depends(
        Provide[AppContainer.connection_info_package.connection_info_service])
):
    tenant_id = request.user.tenant_id
    connection_infos: PagingResult[ConnectionInfo] = await connection_info_service.paging(
        query, tenant_id, True)  # type: ignore
    return connection_infos


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION_INFO])
@inject
async def create(
    request: Request,
    items: List[CreateConnectionInfo] = Body(),
    connection_info_service: ConnectionInfoService = Depends(
        Provide[AppContainer.connection_info_package.connection_info_service])
):
    tenant_id = request.user.tenant_id
    connection_infos = await connection_info_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=connection_infos)
    return result


@router.put("/{connection_info_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION_INFO])
@inject
async def update(
    request: Request,
    connection_info_id: str,
    item: UpdateConnectionInfo = Body(),
    connection_info_service: ConnectionInfoService = Depends(
        Provide[AppContainer.connection_info_package.connection_info_service])
):
    tenant_id = request.user.tenant_id
    connection_info = await connection_info_service.update(connection_info_id, item, tenant_id)
    if connection_info == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[connection_info], affected=1)
    return result


@router.delete("/{connection_info_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION_INFO])
@inject
async def delete(
    request: Request,
    connection_info_id: str,
    connection_info_service: ConnectionInfoService = Depends(
        Provide[AppContainer.connection_info_package.connection_info_service])
):
    tenant_id = request.user.tenant_id
    is_success = await connection_info_service.delete(connection_info_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION_INFO])
@inject
async def delete_by_ids(
    request: Request,
    connection_info_ids: List[str],
    connection_info_service: ConnectionInfoService = Depends(
        Provide[AppContainer.connection_info_package.connection_info_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await connection_info_service.delete_by_ids(connection_info_ids, tenant_id)    
    is_success = True if deleted_count == len(connection_info_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CONNECTION_INFO])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    connection_info_service: ConnectionInfoService = Depends(
        Provide[AppContainer.connection_info_package.connection_info_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await connection_info_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.put("/isconnectlist/", status_code=201, response_model=PagingResult[ConnectionInfo])
@authorize([ApiScopeType.EDIT_CONNECTION_INFO])
@inject
async def isconnectlist(
    request: Request,
    ids :  List[str],
    connection_info_service: ConnectionInfoService = Depends(
        Provide[AppContainer.connection_info_package.connection_info_service])
):
    tenant_id = request.user.tenant_id
    connection_info_list: List[ConnectionInfo] = await connection_info_service.isConnectList(ids, tenant_id) 
    result = PagingResult[ConnectionInfo](
            total=len(connection_info_list),
            items=connection_info_list,
        )
     
    return result
    

@router.put("/isconnect/", status_code=201, response_model=PagingResult[CreateConnectionInfo])
@authorize([ApiScopeType.EDIT_CONNECTION_INFO])
@inject
async def isconnect(
    request: Request,
    items: List[CreateConnectionInfo] = Body(),
    connection_info_service: ConnectionInfoService = Depends(
        Provide[AppContainer.connection_info_package.connection_info_service])
):
    tenant_id = request.user.tenant_id
    connection_info : CreateConnectionInfo = await connection_info_service.isConnect(items[0], tenant_id) 
    
    result = PagingResult[CreateConnectionInfo](
            total=1,
            items=[connection_info],
        )
     
    return result