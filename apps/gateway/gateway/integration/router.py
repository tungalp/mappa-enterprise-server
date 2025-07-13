from ctypes import Array
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID,uuid4
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.gateway.constant import ApiScopeType
from mapa.gateway.integration.integration_model import CreateIntegration, Integration, UpdateIntegration, UpdateAllIntegration
from mapa.gateway.soap.soap_model import SoapEndpoint, SoapModel
from gateway.config.app_container import AppContainer
from mapa.gateway.integration.integration_service import IntegrationService
from mapa.core.data.base_entity import Base
from pydantic import BaseModel
from mapa.security import authorize

router = APIRouter()

@router.get("/{integration_id}", response_model=Integration)
@authorize([ApiScopeType.QUERY_INTEGRATION])
@inject
async def find(
    request: Request,
    integration_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    integration_service: IntegrationService = Depends(
        Provide[AppContainer.integration_package.integration_service])):
    """Integration bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    integration = await integration_service.get(integration_id, tenant_id, field_list)
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return integration


@router.get("/", response_model=PagingResult[Integration])
@authorize([ApiScopeType.EDIT_INTEGRATION])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    integration_service: IntegrationService = Depends(
        Provide[AppContainer.integration_package.integration_service])
):
    tenant_id = request.user.tenant_id
    integrations: PagingResult[Integration] = await integration_service.paging(
        query, tenant_id)  # type: ignore
    return integrations


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INTEGRATION])
@inject
async def create(
    request: Request,
    items: List[CreateIntegration] = Body(),
    integration_service: IntegrationService = Depends(
        Provide[AppContainer.integration_package.integration_service])
):
    tenant_id = request.user.tenant_id
    integrations = await integration_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=integrations)
    return result


@router.put("/{integration_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INTEGRATION])
@inject
async def update(
    request: Request,
    integration_id: str,
    item: UpdateIntegration = Body(),
    integration_service: IntegrationService = Depends(
        Provide[AppContainer.integration_package.integration_service])
):
    tenant_id = request.user.tenant_id
    integration = await integration_service.update(integration_id, item, tenant_id)
    if integration == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[integration], affected=1)
    return result


@router.delete("/{integration_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INTEGRATION])
@inject
async def delete(
    request: Request,
    integration_id: str,
    integration_service: IntegrationService = Depends(
        Provide[AppContainer.integration_package.integration_service])
):
    tenant_id = request.user.tenant_id
    is_success = await integration_service.delete(integration_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INTEGRATION])
@inject
async def delete_by_ids(
    request: Request,
    integration_ids: List[str],
    integration_service: IntegrationService = Depends(
        Provide[AppContainer.integration_package.integration_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await integration_service.delete_by_ids(integration_ids, tenant_id)
    is_success = True if deleted_count == len(integration_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_INTEGRATION])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    integration_service: IntegrationService = Depends(
        Provide[AppContainer.integration_package.integration_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await integration_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.post("/soap_infos", status_code=201, response_model=List[SoapModel])
@authorize([ApiScopeType.EDIT_INTEGRATION])
@inject
async def get_wsdl_infos(
    request: Request,
    soap: SoapEndpoint = Body(),
    integration_service: IntegrationService = Depends(
        Provide[AppContainer.integration_package.integration_service])
):
    """Soap bilgilerini getirir"""
    
    try: 
        tenant_id = request.user.tenant_id
        result = await integration_service.get_soap_infos(tenant_id,soap.wsdl_endpoint, soap.endpoint, soap.connection_info_id)
        if not soap:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Soap Not Found'))
    except Exception as ex:        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))
    

    return result