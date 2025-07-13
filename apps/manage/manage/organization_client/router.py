from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.manage.constants import ApiScopeType
from mapa.manage.organization_client.organization_client_model import CreateOrganizationClient, OrganizationClient, UpdateOrganizationClient
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from manage.config.app_container import AppContainer

router = APIRouter()


@router.get("/{organization_client_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_ORGANIZATION_CLIENT])
@inject
async def find(
    request: Request,
    organization_client_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    organization_client_service: OrganizationClientService = Depends(
        Provide[AppContainer.organization_client_package.organization_client_service])):
    """OrganizationClient bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    organization_client = await organization_client_service.get(organization_client_id, tenant_id, field_list)
    if not organization_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return organization_client


@router.get("/", response_model=PagingResult[OrganizationClient])
@authorize([ApiScopeType.QUERY_ORGANIZATION_CLIENT])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    organization_client_service: OrganizationClientService = Depends(
        Provide[AppContainer.organization_client_package.organization_client_service])
):
    tenant_id = request.user.tenant_id
    organization_clients: PagingResult[OrganizationClient] = await organization_client_service.paging(
        query, tenant_id)  # type: ignore
    return organization_clients


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_CLIENT])
@inject
async def create(
    request: Request,
    items: List[CreateOrganizationClient] = Body(),
    organization_client_service: OrganizationClientService = Depends(
        Provide[AppContainer.organization_client_package.organization_client_service])
):
    tenant_id = request.user.tenant_id
    organization_clients = await organization_client_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=organization_clients)
    return result


@router.put("/{organization_client_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_CLIENT])
@inject
async def update(
    request: Request,
    organization_client_id: str,
    item: UpdateOrganizationClient = Body(),
    organization_client_service: OrganizationClientService = Depends(
        Provide[AppContainer.organization_client_package.organization_client_service])
):
    tenant_id = request.user.tenant_id
    organization_client = await organization_client_service.update(organization_client_id, item, tenant_id)
    if not organization_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[organization_client], affected=1)
    return result


@router.delete("/{organization_client_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_CLIENT])
@inject
async def delete(
    request: Request,
    organization_client_id: str,
    organization_client_service: OrganizationClientService = Depends(
        Provide[AppContainer.organization_client_package.organization_client_service])
):
    tenant_id = request.user.tenant_id
    is_success = await organization_client_service.delete(organization_client_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_CLIENT])
@inject
async def delete_by_ids(
    request: Request,
    organization_client_ids: List[str],
    organization_client_service: OrganizationClientService = Depends(
        Provide[AppContainer.organization_client_package.organization_client_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_client_service.delete_by_ids(organization_client_ids, tenant_id)
    is_success = True if deleted_count == len(organization_client_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION_CLIENT])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    organization_client_service: OrganizationClientService = Depends(
        Provide[AppContainer.organization_client_package.organization_client_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_client_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
