from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.client_api.client_api_model import CreateClientApi, ClientApi, UpdateClientApi, UpdateAllClientApi
from manage.config.app_container import AppContainer
from mapa.manage.client_api.client_api_service import ClientApiService
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

client_api_field_list = [
    "id",
    "client_id",
    "api_id",
    "client.name",
    "client.id",
    "client.grant_types",
    "client.created_at",
    "client.client_id",
    "client.level_type",
    "client.application_type",
    "api.name",
    "api.id",
    "api.identifier",
    "api.level_type",
]

router = APIRouter()


@router.get("/{api_id}", response_model=ClientApi)
@authorize([ApiScopeType.QUERY_CLIENT_API])
@inject
async def find(
    request: Request,
    api_id: str,
    field_list: List[str] = fields_param(),  # type: ignore
    client_api_service: ClientApiService = Depends(
        Provide[AppContainer.client_api_package.client_api_service])):
    """ClientApi bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    if field_list is None:
        field_list = client_api_field_list
    # type: ignore
    client_api = await client_api_service.get(api_id, tenant_id, field_list) # type: ignore
    if not client_api:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    return client_api


@router.get("/", response_model=PagingResult[ClientApi])
@authorize([ApiScopeType.QUERY_CLIENT_API])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    client_api_service: ClientApiService = Depends(
        Provide[AppContainer.client_api_package.client_api_service])
):
    tenant_id = request.user.tenant_id
    if query.select is None:
        query.select = client_api_field_list
    client_apis: PagingResult[ClientApi] = await client_api_service.paging(
        query, tenant_id)  # type: ignore
    return client_apis


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API])
@inject
async def create(
    request: Request,
    items: List[CreateClientApi] = Body(),
    client_api_service: ClientApiService = Depends(
        Provide[AppContainer.client_api_package.client_api_service])
):
    tenant_id = request.user.tenant_id
    client_apis = await client_api_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=client_apis)
    return result


@router.put("/{client_api_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API])
@inject
async def update(
    request: Request,
    client_api_id: str,
    item: UpdateClientApi = Body(),
    client_api_service: ClientApiService = Depends(
        Provide[AppContainer.client_api_package.client_api_service])
):
    tenant_id = request.user.tenant_id
    client_api = await client_api_service.update(client_api_id, item, tenant_id)
    if not client_api:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[client_api], affected=1)
    return result


@router.delete("/{client_api_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API])
@inject
async def delete(
    request: Request,
    client_api_id: str,
    client_api_service: ClientApiService = Depends(
        Provide[AppContainer.client_api_package.client_api_service])
):
    tenant_id = request.user.tenant_id
    is_success = await client_api_service.delete(client_api_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API])
@inject
async def delete_by_ids(
    request: Request,
    client_api_ids: List[str],
    client_api_service: ClientApiService = Depends(
        Provide[AppContainer.client_api_package.client_api_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await client_api_service.delete_by_ids(client_api_ids, tenant_id)
    is_success = True if deleted_count == len(client_api_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    client_api_service: ClientApiService = Depends(
        Provide[AppContainer.client_api_package.client_api_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await client_api_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
