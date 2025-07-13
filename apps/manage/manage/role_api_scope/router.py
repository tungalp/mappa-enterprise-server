from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.role_api_scope.role_api_scope_model import CreateRoleApiScope, RoleApiScope,UpdateAllRoleApiScope,UpdateRoleApiScope
from manage.config.app_container import AppContainer
from mapa.manage.role_api_scope.role_api_scope_service import RoleApiScopeService
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

router = APIRouter()
@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_API_SCOPE])
@inject
async def create(
    request: Request,
    items: List[CreateRoleApiScope] = Body(),
    role_api_scope_api_scope_service: RoleApiScopeService = Depends(
        Provide[AppContainer.role_api_scope_package.role_api_scope_service])
):
    tenant_id = request.user.tenant_id
    role_api_scopes = await role_api_scope_api_scope_service.create_all(items, tenant_id)
    result = ActionResult(success=True,items=role_api_scopes)
    return result

   
@router.get("/{role_api_scope_id}", response_model=RoleApiScope)
@authorize([ApiScopeType.QUERY_ROLE_API_SCOPE])
@inject
async def find(
    request: Request,
    role_api_scope_id: UUID,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    role_api_scope_service: RoleApiScopeService = Depends(
        Provide[AppContainer.role_api_scope_package.role_api_scope_service])):
    """RoleApiScope bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    role_api_scope = await role_api_scope_service.get(role_api_scope_id, tenant_id,field_list)
    if not role_api_scope:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return role_api_scope


@router.get("/", response_model=PagingResult[RoleApiScope])
@authorize([ApiScopeType.QUERY_ROLE_API_SCOPE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    role_api_scope_service: RoleApiScopeService = Depends(
        Provide[AppContainer.role_api_scope_package.role_api_scope_service])
):
    tenant_id = request.user.tenant_id
    role_api_scopes: PagingResult[RoleApiScope] = await role_api_scope_service.paging(
        query, tenant_id)  # type: ignore
    return role_api_scopes


@router.put("/{role_api_scope_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_API_SCOPE])
@inject
async def update(
    request: Request,
    role_api_scope_id: str,
    item: UpdateRoleApiScope = Body(),
    role_api_scope_service: RoleApiScopeService = Depends(
        Provide[AppContainer.role_api_scope_package.role_api_scope_service])
):
    tenant_id = request.user.tenant_id
    role_api_scope = await role_api_scope_service.update(role_api_scope_id, item, tenant_id)
    if not role_api_scope:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[role_api_scope], affected=1)
    return JSONResponse(content=result.model_dump())


@router.delete("/{role_api_scope_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_API_SCOPE])
@inject
async def delete(
    request: Request,
    role_api_scope_id: UUID,
    role_api_scope_service: RoleApiScopeService = Depends(
        Provide[AppContainer.role_api_scope_package.role_api_scope_service])
):
    tenant_id = request.user.tenant_id
    is_success = await role_api_scope_service.delete(role_api_scope_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.delete("/{role_api_scopes_ids}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_API_SCOPE])
@inject
async def delete_by_ids(
    request: Request,
    role_api_scopes_ids: Any,
    role_api_scope_service: RoleApiScopeService = Depends(
        Provide[AppContainer.role_api_scope_package.role_api_scope_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await role_api_scope_service.delete_by_ids(role_api_scopes_ids, tenant_id)
    is_success = True if deleted_count == len(role_api_scopes_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_API_SCOPE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    role_api_scope_service: RoleApiScopeService = Depends(
        Provide[AppContainer.role_api_scope_package.role_api_scope_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await role_api_scope_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
    
    