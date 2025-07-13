from typing import Any, Dict, List
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult,PagingResult
from mapa.manage.role.role_model import CreateRole, Role, UpdateAllRole, UpdateRole
from manage.config.app_container import AppContainer
from mapa.manage.role.role_service import RoleService
from mapa.manage.constants import ApiScopeType
from mapa.security import authorize

router = APIRouter()
@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE])
@inject
async def create(
    request: Request,
    items: List[CreateRole] = Body(),
    role_service: RoleService = Depends(
        Provide[AppContainer.role_package.role_service])
):
    tenant_id = request.user.tenant_id
    roles = await role_service.create_all(items, tenant_id)
    result = ActionResult(success=True,items=roles)
    return result
    
@router.get("/{role_id}", response_model=Role)
@authorize([ApiScopeType.QUERY_ROLE])
@inject
async def find(
    request: Request,
    role_id: UUID,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    role_service: RoleService = Depends(
        Provide[AppContainer.role_package.role_service])):
    """Role bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    role = await role_service.get(role_id, tenant_id,field_list)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    return role


@router.get("/", response_model=PagingResult[Role])
@authorize([ApiScopeType.QUERY_ROLE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    role_service: RoleService = Depends(
        Provide[AppContainer.role_package.role_service])
):
    tenant_id = request.user.tenant_id
    roles: PagingResult[Role] = await role_service.paging(
        query, tenant_id)  # type: ignore
    return roles


@router.put("/{role_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE])
@inject
async def update(
    request: Request,
    role_id: str,
    item: UpdateRole = Body(),
    role_service: RoleService = Depends(
        Provide[AppContainer.role_package.role_service])
):
    tenant_id = request.user.tenant_id
    role = await role_service.update(role_id, item, tenant_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[role], affected=1)
    return result

@router.put("/updateAll/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE])
@inject
async def updateAll(
    request: Request,
    query: QueryArgs = query_param(),
    item: UpdateAllRole = Body(),
    role_service: RoleService = Depends(
        Provide[AppContainer.role_package.role_service])
):
    tenant_id = request.user.tenant_id
    count = len([sec for frst in query.where for sec in frst.value])  # type: ignore  
    updateCount = await role_service.update_all(query, item, tenant_id)
    is_success = True if updateCount == count else False  
    result = ActionResult(success=is_success, affected=updateCount)
    return JSONResponse(content=result.model_dump())

@router.delete("/{role_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE])
@inject
async def delete(
    request: Request,
    role_id: UUID,
    role_service: RoleService = Depends(
        Provide[AppContainer.role_package.role_service])
):
    tenant_id = request.user.tenant_id
    is_success = await role_service.delete(role_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE])
@inject
async def delete_by_ids(
    request: Request,
    role_ids: List[str],
    role_service: RoleService = Depends(
        Provide[AppContainer.role_package.role_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await role_service.delete_by_ids(role_ids, tenant_id)
    is_success = True if deleted_count == len(role_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROLE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    role_service: RoleService = Depends(
        Provide[AppContainer.role_package.role_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await role_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())