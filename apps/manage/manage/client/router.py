from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.client.client_model import ClientInfo, CreateClient, Client, UpdateClient, UpdateAllClient
from manage.config.app_container import AppContainer
from mapa.manage.client.client_service import ClientService
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

router = APIRouter()

# @router.get("/{client_id}", response_model=Client)
# @authorize([ApiScopeType.QUERY_CLIENT])
# @inject
# async def get_by_client_id(
#     request: Request,
#     client_id: str,
#     client_service: ClientService = Depends(
#         Provide[AppContainer.client_package.client_service])):
#     """Client bilgilerini getirir"""

#     tenant_id = request.user.tenant_id
#     client = await client_service.get_by_client_id(client_id, tenant_id)
#     if not client:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
#     return client

@router.get("/info/{client_id}", response_model=ClientInfo)
@inject
async def get_info(
    request: Request,
    client_id: str,
    client_service: ClientService = Depends(
        Provide[AppContainer.client_package.client_service])):
    """Genel Client bilgilerini getirir"""

    client_info = await client_service.get_client_info(client_id)
    if not client_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return client_info


@router.get("/{id}", response_model=Client)
@authorize([ApiScopeType.QUERY_CLIENT])
@inject
async def find(
    request: Request,
    id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    client_service: ClientService = Depends(
        Provide[AppContainer.client_package.client_service])):
    """Client bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    client = await client_service.get(id, tenant_id, field_list) # type: ignore
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return client


@router.get("/", response_model=PagingResult[Client])
@authorize([ApiScopeType.QUERY_CLIENT])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    client_service: ClientService = Depends(
        Provide[AppContainer.client_package.client_service])
):
    tenant_id = request.user.tenant_id
    clients: PagingResult[Client] = await client_service.paging(
        query, tenant_id)  # type: ignore
    return clients


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT])
@inject
async def create(
    request: Request,
    items: List[CreateClient] = Body(),
    client_service: ClientService = Depends(
        Provide[AppContainer.client_package.client_service])
):
    tenant_id = request.user.tenant_id
    clients = await client_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=clients)
    return result


@router.put("/{client_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT])
@inject
async def update(
    request: Request,
    client_id: str,
    item: UpdateClient = Body(),
    client_service: ClientService = Depends(
        Provide[AppContainer.client_package.client_service])
):
    tenant_id = request.user.tenant_id
    client = await client_service.update(client_id, item, tenant_id)
    result = ActionResult(success=True, items=[client], affected=1)
    return result


@router.delete("/{client_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT])
@inject
async def delete(
    request: Request,
    client_id: str,
    client_service: ClientService = Depends(
        Provide[AppContainer.client_package.client_service])
):
    tenant_id = request.user.tenant_id
    is_success = await client_service.delete(client_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT])
@inject
async def delete_by_ids(
    request: Request,
    client_ids:  List[str],
    client_service: ClientService = Depends(
        Provide[AppContainer.client_package.client_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await client_service.delete_by_ids(client_ids, tenant_id)
    is_success = True if deleted_count == len(client_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    client_service: ClientService = Depends(
        Provide[AppContainer.client_package.client_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await client_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())

