from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime, timedelta
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.role_user.role_user_model import CreateRoleUser, RoleUser,UpdateAllRoleUser,UpdateRoleUser
from manage.config.app_container import AppContainer
from mapa.manage.role_user.role_user_service import RoleUserService
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

router = APIRouter()
@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_USER])
@inject
async def create(
    request: Request,
    items: List[CreateRoleUser] = Body(),
    role_user_service: RoleUserService = Depends(
        Provide[AppContainer.role_user_package.role_user_service])
):
    tenant_id = request.user.tenant_id
    for i in items:
        i.expired_at = datetime.now() + timedelta(days=10)
        
    role_users = await role_user_service.create_all(items, tenant_id)
    result = ActionResult(success=True,items=role_users)
    return result

    
@router.get("/{role_user_id}", response_model=RoleUser)
@authorize([ApiScopeType.QUERY_ROLE_USER])
@inject
async def find(
    request: Request,
    role_user_id: UUID,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    role_user_service: RoleUserService = Depends(
        Provide[AppContainer.role_user_package.role_user_service])):
    """RoleUser bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    role_user = await role_user_service.get(role_user_id, tenant_id,field_list)
    if not role_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return role_user


@router.get("/", response_model=PagingResult[RoleUser])
@authorize([ApiScopeType.QUERY_ROLE_USER])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    role_user_service: RoleUserService = Depends(
        Provide[AppContainer.role_user_package.role_user_service])
):
    tenant_id = request.user.tenant_id
    role_users: PagingResult[RoleUser] = await role_user_service.paging(
        query, tenant_id)  # type: ignore
    return role_users


@router.put("/{role_user_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_USER])
@inject
async def update(
    request: Request,
    role_user_id: str,
    item: UpdateRoleUser = Body(),
    role_user_service: RoleUserService = Depends(
        Provide[AppContainer.role_user_package.role_user_service])
):
    tenant_id = request.user.tenant_id
    role_user = await role_user_service.update(role_user_id, item, tenant_id)
    if not role_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[role_user], affected=1)
    return JSONResponse(content=result.model_dump())


@router.delete("/{role_user_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_USER])
@inject
async def delete(
    request: Request,
    role_user_id: UUID,
    role_user_service: RoleUserService = Depends(
        Provide[AppContainer.role_user_package.role_user_service])
):
    tenant_id = request.user.tenant_id
    is_success = await role_user_service.delete(role_user_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.delete("/{role_users_ids}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_USER])
@inject
async def delete_by_ids(
    request: Request,
    role_users_ids: Any,
    role_user_service: RoleUserService = Depends(
        Provide[AppContainer.role_user_package.role_user_service])
):
    tenant_id = request.user.tenant_id
    delete_count = await role_user_service.delete_by_ids(role_users_ids, tenant_id)
    is_success = True if delete_count == len(role_users_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=delete_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE_USER])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    role_user_service: RoleUserService = Depends(
        Provide[AppContainer.role_user_package.role_user_service])
):
    tenant_id = request.user.tenant_id
    delete_count = await role_user_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=delete_count)
    return JSONResponse(content=result.model_dump())
    
    

