from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.manage.constants import ApiScopeType
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType, OrganizationType, UpdateOrganizationType
from mapa.manage.organization_type.organization_type_service import OrganizationTypeService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from manage.config.app_container import AppContainer

router = APIRouter()


@router.get("/{organization_type_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_ORGANIZATION_TYPE])
@inject
async def find(
    request: Request,
    organization_type_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    organization_type_service: OrganizationTypeService = Depends(
        Provide[AppContainer.organization_type_package.organization_type_service])):
    """OrganizationType bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    organization_type = await organization_type_service.get(organization_type_id, tenant_id, field_list)
    if not organization_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return organization_type


@router.get("/", response_model=PagingResult[OrganizationType])
@authorize([ApiScopeType.QUERY_ORGANIZATION_TYPE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    organization_type_service: OrganizationTypeService = Depends(
        Provide[AppContainer.organization_type_package.organization_type_service])
):
    tenant_id = request.user.tenant_id
    organization_types: PagingResult[OrganizationType] = await organization_type_service.paging(
        query, tenant_id)  # type: ignore
    return organization_types


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_TYPE])
@inject
async def create(
    request: Request,
    items: List[CreateOrganizationType] = Body(),
    organization_type_service: OrganizationTypeService = Depends(
        Provide[AppContainer.organization_type_package.organization_type_service])
):
    tenant_id = request.user.tenant_id
    organization_types = await organization_type_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=organization_types)
    return result


@router.put("/{organization_type_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_TYPE])
@inject
async def update(
    request: Request,
    organization_type_id: str,
    item: UpdateOrganizationType = Body(),
    organization_type_service: OrganizationTypeService = Depends(
        Provide[AppContainer.organization_type_package.organization_type_service])
):
    tenant_id = request.user.tenant_id
    organization_type = await organization_type_service.update(organization_type_id, item, tenant_id)
    if not organization_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[organization_type], affected=1)
    return result


@router.delete("/{organization_type_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_TYPE])
@inject
async def delete(
    request: Request,
    organization_type_id: str,
    organization_type_service: OrganizationTypeService = Depends(
        Provide[AppContainer.organization_type_package.organization_type_service])
):
    tenant_id = request.user.tenant_id
    is_success = await organization_type_service.delete(organization_type_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_TYPE])
@inject
async def delete_by_ids(
    request: Request,
    organization_type_ids: List[str],
    organization_type_service: OrganizationTypeService = Depends(
        Provide[AppContainer.organization_type_package.organization_type_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_type_service.delete_by_ids(organization_type_ids, tenant_id)
    is_success = True if deleted_count == len(organization_type_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_TYPE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    organization_type_service: OrganizationTypeService = Depends(
        Provide[AppContainer.organization_type_package.organization_type_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_type_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
