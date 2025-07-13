from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import Filter, QueryArgs, FilterOp
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.client_api_scope.client_api_scope_model import CreateClientApiScope, ClientApiScope, UpdateClientApiScope, UpdateAllClientApiScope
from manage.config.app_container import AppContainer
from mapa.manage.client_api_scope.client_api_scope_service import ClientApiScopeService
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

router = APIRouter()

@router.get("/{api_id}", response_model=ClientApiScope)
@authorize([ApiScopeType.QUERY_CLIENT_API_SCOPE])
@inject
async def find(
    request: Request,
    api_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    client_api_scope_service: ClientApiScopeService = Depends(
        Provide[AppContainer.client_api_scope_package.client_api_scope_service])):
    """ClientApiScope bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    client_api_scope = await client_api_scope_service.get(api_id, tenant_id, field_list)
    if not client_api_scope:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))


    return client_api_scope


@router.get("/", response_model=PagingResult[ClientApiScope])
@authorize([ApiScopeType.QUERY_CLIENT_API_SCOPE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    client_api_scope_service: ClientApiScopeService = Depends(
        Provide[AppContainer.client_api_scope_package.client_api_scope_service])
):
    tenant_id = request.user.tenant_id
    client_api_scopes: PagingResult[ClientApiScope] = await client_api_scope_service.paging(
        query, tenant_id)  # type: ignore
    return client_api_scopes


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API_SCOPE])
@inject
async def create(
    request: Request,
    items: List[CreateClientApiScope] = Body(),
    client_api_scope_service: ClientApiScopeService = Depends(
        Provide[AppContainer.client_api_scope_package.client_api_scope_service])
):
    tenant_id = request.user.tenant_id
    client_api_scopes = await client_api_scope_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=client_api_scopes)
    return result


@router.put("/{client_api_scope_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API_SCOPE])
@inject
async def update(
    request: Request,
    client_api_scope_id: str,
    item: UpdateClientApiScope = Body(),
    client_api_scope_service: ClientApiScopeService = Depends(
        Provide[AppContainer.client_api_scope_package.client_api_scope_service])
):
    tenant_id = request.user.tenant_id
    client_api_scope = await client_api_scope_service.update(client_api_scope_id, item, tenant_id)
    if not client_api_scope:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[client_api_scope], affected=1)
    return result


@router.delete("/{client_api_scope_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API_SCOPE])
@inject
async def delete(
    request: Request,
    client_api_scope_id: str,
    client_api_scope_service: ClientApiScopeService = Depends(
        Provide[AppContainer.client_api_scope_package.client_api_scope_service])
):
    tenant_id = request.user.tenant_id
    is_success = await client_api_scope_service.delete(client_api_scope_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API_SCOPE])
@inject
async def delete_by_ids(
    request: Request,
    client_api_scope_ids: List[str],
    client_api_scope_service: ClientApiScopeService = Depends(
        Provide[AppContainer.client_api_scope_package.client_api_scope_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await client_api_scope_service.delete_by_ids(client_api_scope_ids, tenant_id)
    is_success = True if deleted_count == len(client_api_scope_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API_SCOPE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    client_api_scope_service: ClientApiScopeService = Depends(
        Provide[AppContainer.client_api_scope_package.client_api_scope_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await client_api_scope_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.post("/recreate", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API_SCOPE])
@inject
async def recreate(
    request: Request,
    items: List[CreateClientApiScope] = Body(),
    client_api_scope_service: ClientApiScopeService = Depends(
        Provide[AppContainer.client_api_scope_package.client_api_scope_service])
):
    tenant_id = request.user.tenant_id
    client_api_scopes = await client_api_scope_service.recreate(items, tenant_id)
    result = ActionResult(success=True, items=client_api_scopes)
    return result


@router.put("/delete_by_client_api_id/{client_api_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_CLIENT_API_SCOPE])
@inject
async def delete_by_client_api_id(
    request: Request,
    client_api_id: str,
    client_api_scope_service: ClientApiScopeService = Depends(
        Provide[AppContainer.client_api_scope_package.client_api_scope_service])
):
    tenant_id = request.user.tenant_id
    queryArgs = QueryArgs(
            where=[
                Filter(field="client_api_id",
                       op=FilterOp.EQUAL, value=client_api_id) # type: ignore  
           ]
        )
    
    deleted_count = await client_api_scope_service.delete_all(queryArgs, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())