from typing import List
from dependency_injector.wiring import Provide, inject
from mapa.manage.tenant_user.tenant_user_model import TenantUserRole
from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.tenant.tenant_model import Tenant, UpdateTenant
from mapa.manage.tenant.tenant_service import TenantService
from mapa.manage.tenant_user.tenant_user_service import TenantUserService
from mapa.security.authorize import authorize
from manage.config.app_container import AppContainer
from mapa.core.data.result import ActionResult, PagingResult
from mapa.manage.constants import ApiScopeType
from mapa.app.params import fields_param, query_param

router = APIRouter()


@router.get("/{tenant_id}", response_model=Tenant)
@inject
async def find(
    tenant_id: str,
    tenant_service: TenantService = Depends(
        Provide[AppContainer.tenant_package.tenant_service])):
    """Genel Client bilgilerini getirir"""
    tenant = await tenant_service.get(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return tenant



@router.get("/find_by_tenant_name/{tenant_name}", response_model=Tenant)
@inject
async def find_by_tenant_name(
    tenant_name: str,
    tenant_service: TenantService = Depends(
        Provide[AppContainer.tenant_package.tenant_service])
):
    query_args: QueryArgs = QueryArgs(where=[
        Filter(field="name", op=FilterOp.ILIKE, value=tenant_name),
    ])
    tenant_list: PagingResult[Tenant] = await tenant_service.paging(query_args)  # type: ignore
    if not tenant_list.items or not tenant_list.items[0]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return tenant_list.items[0]



@router.get("/find_by_tenant_id/{tenant_id}", response_model=Tenant)
@inject
async def find_by_tenant_id(
    tenant_id: str,
    tenant_service: TenantService = Depends(
        Provide[AppContainer.tenant_package.tenant_service])
):
    query_args: QueryArgs = QueryArgs(where=[
        Filter(field="id", op=FilterOp.EQUAL, value=tenant_id),
    ])
    tenant_list: PagingResult[Tenant] = await tenant_service.paging(query_args)  # type: ignore
    if not tenant_list.items or not tenant_list.items[0]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return tenant_list.items[0]


@router.get("/", response_model=List[Tenant])
@inject
@authorize()
async def get(
    request: Request,
    tenant_service: TenantService = Depends(
        Provide[AppContainer.tenant_package.tenant_service]),
    tenant_user_service: TenantUserService = Depends(
        Provide[AppContainer.tenant_package.tenant_user_service]),

):
    """Tenant bilgilerini getirir"""
    user_id = request.user.sub
    tenant_user_list = await tenant_user_service.find_by_user_id(user_id)
    
    query_args: QueryArgs = QueryArgs(
        limit=0,
        offset=0,
        where=[
            Filter(field="id", op=FilterOp.IN, value=[
                tenant_user.tenant_id for tenant_user in tenant_user_list
            ])
        ])
    
    tenant_list = await tenant_service.paging(query_args)

    return JSONResponse(content=jsonable_encoder(tenant_list.items))


@router.get("/owner_tenant/", response_model=Tenant)
@inject
@authorize()
async def owner_tenant(
    request: Request,
    tenant_service: TenantService = Depends(
        Provide[AppContainer.tenant_package.tenant_service]),
    tenant_user_service: TenantUserService = Depends(
        Provide[AppContainer.tenant_package.tenant_user_service]),

):
    """Owner Tenant bilgilerini getirir"""
    user_id = request.user.sub
    tenant_user_list = await tenant_user_service.find_by_user_id(user_id)
    tenant_user_list = [
        tenant_user for tenant_user in tenant_user_list if tenant_user.role == TenantUserRole.OWNER]
    tenant_user = tenant_user_list[0]
    tenant = await tenant_service.find_one(query_args=QueryArgs(
        where=[
            Filter(field="id", op=FilterOp.EQUAL, value=tenant_user.tenant_id)
        ]
    ))

    return JSONResponse(content=jsonable_encoder(tenant))


@router.put("/{tenant_id}", status_code=201, response_model=ActionResult)
@inject
@authorize()
async def update(
    request: Request,
    tenant_id: str,
    item: UpdateTenant = Body(),
    tenant_service: TenantService = Depends(
        Provide[AppContainer.tenant_package.tenant_service])
):
    """ Tenant bilgilerini günceller"""
    tenant = await tenant_service.update(tenant_id, item, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[tenant], affected=1)
    return result
