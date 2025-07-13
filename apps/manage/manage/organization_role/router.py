from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.manage.constants import ApiScopeType
from mapa.manage.organization_role.organization_role_model import CreateOrganizationRole, OrganizationRole, UpdateOrganizationRole
from mapa.manage.organization_role.organization_role_service import OrganizationRoleService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from manage.config.app_container import AppContainer

router = APIRouter()


@router.get("/{organization_role_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_ORGANIZATION_ROLE])
@inject
async def find(
    request: Request,
    organization_role_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    organization_role_service: OrganizationRoleService = Depends(
        Provide[AppContainer.organization_role_package.organization_role_service])):
    """OrganizationRole bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    organization_role = await organization_role_service.get(organization_role_id, tenant_id, field_list)
    if not organization_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return organization_role


@router.get("/", response_model=PagingResult[OrganizationRole])
@authorize([ApiScopeType.QUERY_ORGANIZATION_ROLE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    organization_role_service: OrganizationRoleService = Depends(
        Provide[AppContainer.organization_role_package.organization_role_service])
):
    tenant_id = request.user.tenant_id
    organization_roles: PagingResult[OrganizationRole] = await organization_role_service.paging(
        query, tenant_id)  # type: ignore
    return organization_roles


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_ROLE])
@inject
async def create(
    request: Request,
    items: List[CreateOrganizationRole] = Body(),
    organization_role_service: OrganizationRoleService = Depends(
        Provide[AppContainer.organization_role_package.organization_role_service])
):
    tenant_id = request.user.tenant_id
    organization_roles = await organization_role_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=organization_roles)
    return result


@router.put("/{organization_role_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_ROLE])
@inject
async def update(
    request: Request,
    organization_role_id: str,
    item: UpdateOrganizationRole = Body(),
    organization_role_service: OrganizationRoleService = Depends(
        Provide[AppContainer.organization_role_package.organization_role_service])
):
    tenant_id = request.user.tenant_id
    organization_role = await organization_role_service.update(organization_role_id, item, tenant_id)
    if not organization_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[organization_role], affected=1)
    return result


@router.delete("/{organization_role_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_ROLE])
@inject
async def delete(
    request: Request,
    organization_role_id: str,
    organization_role_service: OrganizationRoleService = Depends(
        Provide[AppContainer.organization_role_package.organization_role_service])
):
    tenant_id = request.user.tenant_id
    is_success = await organization_role_service.delete(organization_role_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_ROLE])
@inject
async def delete_by_ids(
    request: Request,
    organization_role_ids: List[str],
    organization_role_service: OrganizationRoleService = Depends(
        Provide[AppContainer.organization_role_package.organization_role_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_role_service.delete_by_ids(organization_role_ids, tenant_id)
    is_success = True if deleted_count == len(organization_role_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_ROLE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    organization_role_service: OrganizationRoleService = Depends(
        Provide[AppContainer.organization_role_package.organization_role_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_role_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
