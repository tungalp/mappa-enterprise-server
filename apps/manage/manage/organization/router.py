from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.manage.constants import ApiScopeType 
from mapa.manage.organization.organization_model import CreateOrganization, Organization, UpdateOrganization,OrganizationEndpoint
from mapa.manage.organization.organization_service import OrganizationService
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from manage.config.app_container import AppContainer

router = APIRouter()


@router.get("/{organization_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_ORGANIZATION])
@inject
async def find(
    request: Request,
    organization_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])):
    """Organization bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    organization = await organization_service.get(organization_id, tenant_id, field_list)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return organization

# sorgulama işlemi yapıldığında bulunan kayıtların parent bilgileride bulunmaktadır.
# Organization ana page componentinde sorgu için kullanılır.
@router.get("/hierarchicalPaging/", response_model=PagingResult[Organization])
@authorize([ApiScopeType.QUERY_ORGANIZATION])
@inject
async def hierarchicalPaging(
    request: Request,
    query: QueryArgs = query_param(),
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])
):
    tenant_id = request.user.tenant_id
    organizations: PagingResult[Organization] = await organization_service.hierarchical_paging(
        query, tenant_id)  # type: ignore
    return organizations


@router.get("/", response_model=PagingResult[Organization])
@authorize([ApiScopeType.QUERY_ORGANIZATION])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])
):
    tenant_id = request.user.tenant_id
    organizations: PagingResult[Organization] = await organization_service.paging(
        query, tenant_id)  # type: ignore
    return organizations


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION])
@inject
async def create(
    request: Request,
    items: List[CreateOrganization] = Body(),
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])
):
    tenant_id = request.user.tenant_id
    organizations = await organization_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=organizations)
    return result


@router.put("/{organization_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION])
@inject
async def update(
    request: Request,
    organization_id: str,
    item: UpdateOrganization = Body(),
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])
):
    tenant_id = request.user.tenant_id
    organization = await organization_service.update(organization_id, item, tenant_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[organization], affected=1)
    return result


@router.delete("/{organization_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION])
@inject
async def delete(
    request: Request,
    organization_id: str,
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])
):
    tenant_id = request.user.tenant_id
    is_success = await organization_service.delete(organization_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION])
@inject
async def delete_by_ids(
    request: Request,
    organization_ids: List[str],
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_service.delete_by_ids(organization_ids, tenant_id)
    is_success = True if deleted_count == len(organization_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ORGANIZATION])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await organization_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


## first party kısmında kullanılabilen hiyerarşik organization sorgulama methodu.
@router.get("/hierarchical_organization_by_client_id/{client_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_ORGANIZATION])
@inject
async def get_hierarchical_organization_by_client_id(
    request: Request,
    client_id: str,
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])):
    """Client id bilgisine göre Hierarchical Organization bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    organization = await organization_service.get_hierarchical_organization_by_client_id(client_id, tenant_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return organization

## Second ve Third Party uygulamaların hiyerarşik organization bilgilerini sorgulayacağı method.
## Parametere olarak client id ve tenant id bilgilerini bir obje içerisinde yollaması gerekmektedir.
@router.post("/hierarchical_organization_by_end_point")
@inject
async def hierarchical_organization_by_end_point(
    request: Request,
    data: OrganizationEndpoint,
    organization_service: OrganizationService = Depends(
        Provide[AppContainer.organization_package.organization_service])):
    """Client id ve Tenant id bilgisine göre Hierarchical Organization bilgilerini getirir"""

    organization = await organization_service.get_hierarchical_organization_by_client_id(data.client_id, data.info_id, data.tenant_id)
    return organization