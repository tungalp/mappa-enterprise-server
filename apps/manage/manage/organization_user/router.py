from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.manage.constants import ApiScopeType
from mapa.manage.organization_user.organization_user_model import CreateOrganizationUser, OrganizationUser, UpdateOrganizationUser
from mapa.manage.organization_user.organization_user_service import OrganizationUserService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from manage.config.app_container import AppContainer

router = APIRouter()


@router.get("/{organization_user_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_ORGANIZATION_USER])
@inject
async def find(
    request: Request,
    organization_user_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    organization_user_service: OrganizationUserService = Depends(
        Provide[AppContainer.organization_user_package.organization_user_service])):
    """OrganizationUser bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    organization_user = await organization_user_service.get(organization_user_id, tenant_id, field_list)
    if not organization_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return organization_user


@router.get("/", response_model=PagingResult[OrganizationUser])
@authorize([ApiScopeType.QUERY_ORGANIZATION_USER])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    organization_user_service: OrganizationUserService = Depends(
        Provide[AppContainer.organization_user_package.organization_user_service])
):
    tenant_id = request.user.tenant_id
    organization_users: PagingResult[OrganizationUser] = await organization_user_service.paging(
        query, tenant_id)  # type: ignore
    return organization_users


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_USER])
@inject
async def create(
    request: Request,
    items: List[CreateOrganizationUser] = Body(),
    organization_user_service: OrganizationUserService = Depends(
        Provide[AppContainer.organization_user_package.organization_user_service])
):
    tenant_id = request.user.tenant_id
    organization_users = await organization_user_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=organization_users)
    return result


@router.put("/{organization_user_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_USER])
@inject
async def update(
    request: Request,
    organization_user_id: str,
    item: UpdateOrganizationUser = Body(),
    organization_user_service: OrganizationUserService = Depends(
        Provide[AppContainer.organization_user_package.organization_user_service])
):
    tenant_id = request.user.tenant_id
    organization_user = await organization_user_service.update(organization_user_id, item, tenant_id)
    if not organization_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[organization_user], affected=1)
    return result


@router.delete("/{organization_user_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_USER])
@inject
async def delete(
    request: Request,
    organization_user_id: str,
    organization_user_service: OrganizationUserService = Depends(
        Provide[AppContainer.organization_user_package.organization_user_service])
):
    tenant_id = request.user.tenant_id
    is_success = await organization_user_service.delete(organization_user_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_USER])
@inject
async def delete_by_ids(
    request: Request,
    organization_user_ids: List[str],
    organization_user_service: OrganizationUserService = Depends(
        Provide[AppContainer.organization_user_package.organization_user_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_user_service.delete_by_ids(organization_user_ids, tenant_id)
    is_success = True if deleted_count == len(organization_user_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_USER])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    organization_user_service: OrganizationUserService = Depends(
        Provide[AppContainer.organization_user_package.organization_user_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_user_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
