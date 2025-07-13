from ctypes import Array
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.gateway.constant import ApiScopeType
from mapa.gateway.parameter_mapping.parameter_mapping_model import CreateParameterMapping, ParameterMapping, UpdateParameterMapping, UpdateAllParameterMapping
from gateway.config.app_container import AppContainer
from mapa.gateway.parameter_mapping.parameter_mapping_service import ParameterMappingService
from mapa.core.data.base_entity import Base
from pydantic import BaseModel
from mapa.security import authorize

router = APIRouter()


@router.get("/{parameter_mapping_id}", response_model=ParameterMapping)
@authorize([ApiScopeType.QUERY_PARAMETER_MAPPING])
@inject
async def find(
    request: Request,
    parameter_mapping_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    parameter_mapping_service: ParameterMappingService = Depends(
        Provide[AppContainer.parameter_mapping_package.parameter_mapping_service])):
    """IntegrationParameterMapping bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    parameter_mapping = await parameter_mapping_service.get(parameter_mapping_id, tenant_id, field_list)
    if not parameter_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return parameter_mapping


@router.get("/", response_model=PagingResult[ParameterMapping])
@authorize([ApiScopeType.QUERY_PARAMETER_MAPPING])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    parameter_mapping_service: ParameterMappingService = Depends(
        Provide[AppContainer.parameter_mapping_package.parameter_mapping_service])
):
    tenant_id = request.user.tenant_id
    parameter_mappings: PagingResult[ParameterMapping] = await parameter_mapping_service.paging(
        query, tenant_id)  # type: ignore
    return parameter_mappings


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PARAMETER_MAPPING])
@inject
async def create(
    request: Request,
    items: List[CreateParameterMapping] = Body(),
    parameter_mapping_service: ParameterMappingService = Depends(
        Provide[AppContainer.parameter_mapping_package.parameter_mapping_service])
):
    tenant_id = request.user.tenant_id
    parameter_mappings = await parameter_mapping_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=parameter_mappings)
    return result


@router.put("/{parameter_mapping_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PARAMETER_MAPPING])
@inject
async def update(
    request: Request,
    parameter_mapping_id: str,
    item: UpdateParameterMapping = Body(),
    parameter_mapping_service: ParameterMappingService = Depends(
        Provide[AppContainer.parameter_mapping_package.parameter_mapping_service])
):
    tenant_id = request.user.tenant_id
    parameter_mapping = await parameter_mapping_service.update(parameter_mapping_id, item, tenant_id)
    if not parameter_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[
                          parameter_mapping], affected=1)
    return result


@router.delete("/{parameter_mapping_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PARAMETER_MAPPING])
@inject
async def delete(
    request: Request,
    parameter_mapping_id: str,
    parameter_mapping_service: ParameterMappingService = Depends(
        Provide[AppContainer.parameter_mapping_package.parameter_mapping_service])
):
    tenant_id = request.user.tenant_id
    is_success = await parameter_mapping_service.delete(parameter_mapping_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PARAMETER_MAPPING])
@inject
async def delete_by_ids(
    request: Request,
    parameter_mapping_ids: List[str],
    parameter_mapping_service: ParameterMappingService = Depends(
        Provide[AppContainer.parameter_mapping_package.parameter_mapping_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await parameter_mapping_service.delete_by_ids(parameter_mapping_ids, tenant_id)
    is_success = True if deleted_count == len(
        parameter_mapping_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_PARAMETER_MAPPING])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    parameter_mapping_service: ParameterMappingService = Depends(
        Provide[AppContainer.parameter_mapping_package.parameter_mapping_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await parameter_mapping_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
