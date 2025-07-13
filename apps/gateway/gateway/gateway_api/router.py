from typing import Any, List, Dict
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException, Query
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import FilterOp,  QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.gateway.constant import ApiScopeType
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi, ExportGatewayApi,GatewayApi, UpdateGatewayApi
from mapa.gateway.gateway_api.gateway_util_service import GatewayUtilService
from gateway.config.app_container import AppContainer
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService
from mapa.security import authorize

router = APIRouter()

@router.get("/gateway_apis", response_model=List[GatewayApi])
@inject
async def gateway_api(
    query: QueryArgs = query_param(),
    gateway_api_service: GatewayApiService = Depends(
        Provide[AppContainer.gateway_api_package.gateway_api_service])
):
    tenant_id_filter = [x for x in query.where if x.field == 'tenant_id' and x.op==FilterOp.EQUAL] # type: ignore
    if tenant_id_filter is None or len(tenant_id_filter) == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str('Tenant_id filter must be singular and one'))    
    gateway_apis: List[GatewayApi] = await gateway_api_service.find(query, tenant_id_filter[0].value) # type: ignore
    return gateway_apis


@router.get("/{gateway_api_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_GATEWAY_API])
@inject
async def find(
    request: Request,
    gateway_api_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    gateway_api_service: GatewayApiService = Depends(
        Provide[AppContainer.gateway_api_package.gateway_api_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    gateway_api = await gateway_api_service.get(gateway_api_id, tenant_id, field_list)
    if not gateway_api:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return gateway_api


@router.get("/", response_model=PagingResult[GatewayApi])
@authorize([ApiScopeType.QUERY_GATEWAY_API])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    gateway_api_service: GatewayApiService = Depends(
        Provide[AppContainer.gateway_api_package.gateway_api_service])
):
    tenant_id = request.user.tenant_id
    gateway_apis: PagingResult[GatewayApi] = await gateway_api_service.paging(
        query, tenant_id)  # type: ignore
    return gateway_apis


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_GATEWAY_API])
@inject
async def create(
    request: Request,
    items: List[CreateGatewayApi] = Body(),
    gateway_api_service: GatewayApiService = Depends(
        Provide[AppContainer.gateway_api_package.gateway_api_service])
):
    tenant_id = request.user.tenant_id
    gateway_apis = await gateway_api_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=gateway_apis)
    return result


@router.put("/{gateway_api_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_GATEWAY_API])
@inject
async def update(
    request: Request,
    gateway_api_id: str,
    item: UpdateGatewayApi = Body(),
    gateway_api_service: GatewayApiService = Depends(
        Provide[AppContainer.gateway_api_package.gateway_api_service])
):
    tenant_id = request.user.tenant_id
    gateway_api = await gateway_api_service.update(gateway_api_id, item, tenant_id)
    if not gateway_api:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[gateway_api], affected=1)
    return result


@router.delete("/{gateway_api_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_GATEWAY_API])
@inject
async def delete(
    request: Request,
    gateway_api_id: str,
    gateway_api_service: GatewayApiService = Depends(
        Provide[AppContainer.gateway_api_package.gateway_api_service])
):
    tenant_id = request.user.tenant_id
    is_success = await gateway_api_service.delete(gateway_api_id, tenant_id)
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_GATEWAY_API])
@inject
async def delete_by_ids(
    request: Request,
    gateway_api_ids: List[str],
    gateway_api_service: GatewayApiService = Depends(
        Provide[AppContainer.gateway_api_package.gateway_api_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await gateway_api_service.delete_by_ids(gateway_api_ids, tenant_id)
    is_success = True if deleted_count == len(gateway_api_ids) else False
    if is_success == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_GATEWAY_API])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    gateway_api_service: GatewayApiService = Depends(
        Provide[AppContainer.gateway_api_package.gateway_api_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await gateway_api_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.get("/export/gateway_apis", response_model=List[ExportGatewayApi])
@authorize([ApiScopeType.QUERY_GATEWAY_API])
@inject
async def export_gateway_apis(
    request: Request,
    query: QueryArgs = query_param(),
    gateway_util_service: GatewayUtilService = Depends(
        Provide[AppContainer.gateway_package.gateway_util_service])
):
    tenant_id = request.user.tenant_id
    gateway_apis = await gateway_util_service.export_gateway_apis(query, tenant_id)
    return gateway_apis


@router.post("/import/gateway_apis", response_model=ActionResult)
@authorize([ApiScopeType.QUERY_GATEWAY_API])
@inject
async def import_gateway_apis(
    request: Request,
    items: Any = Body(),
    gateway_util_service: GatewayUtilService = Depends(
        Provide[AppContainer.gateway_package.gateway_util_service])
):
      
    try:
        tenant_id = request.user.tenant_id
        gateway_apis = await gateway_util_service.import_gateway_apis(items, tenant_id)
        result = ActionResult(success=True)
        return JSONResponse(content=result.model_dump())
    except ValueError as ex:
        raise ValueError(ex)

@router.get("/export/count")
@authorize([ApiScopeType.QUERY_GATEWAY_API])
@inject
async def count(
    request: Request,
    query: QueryArgs = query_param(),
    gateway_util_service: GatewayUtilService = Depends(
        Provide[AppContainer.gateway_package.gateway_util_service])
):
    tenant_id = request.user.tenant_id
    count: int = await gateway_util_service.count(query, tenant_id)
    return count