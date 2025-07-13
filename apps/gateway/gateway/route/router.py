from ctypes import Array
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID,uuid4
import uuid
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.gateway.constant import ApiScopeType
from mapa.gateway.route.route_model import CreateRoute, Route, UpdateRoute, UpdateAllRoute
from gateway.config.app_container import AppContainer
from mapa.gateway.route.route_service import RouteService
from mapa.core.data.base_entity import Base
from pydantic import BaseModel
from mapa.security import authorize

router = APIRouter()

@router.get("/{route_id}", response_model=Route)
@authorize([ApiScopeType.QUERY_ROUTE])
@inject
async def find(
    request: Request,
    route_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    route_service: RouteService = Depends(
        Provide[AppContainer.route_package.route_service])):
    """Route bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    route = await route_service.get(route_id, tenant_id, field_list)
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))


    return route


@router.get("/", response_model=PagingResult[Route])
@authorize([ApiScopeType.QUERY_ROUTE])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    route_service: RouteService = Depends(
        Provide[AppContainer.route_package.route_service])
):
    tenant_id = request.user.tenant_id
    apis: PagingResult[Route] = await route_service.paging(
        query, tenant_id)  # type: ignore
    return apis


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROUTE])
@inject
async def create(
    request: Request,
    items: List[CreateRoute] = Body(),
    route_service: RouteService = Depends(
        Provide[AppContainer.route_package.route_service])
):
    tenant_id = request.user.tenant_id
    apis = await route_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=apis)
    return result


@router.put("/{route_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROUTE])
@inject
async def update(
    request: Request,
    route_id: str,
    item: UpdateRoute = Body(),
    route_service: RouteService = Depends(
        Provide[AppContainer.route_package.route_service])
):
    tenant_id = request.user.tenant_id
    route = await route_service.update(route_id, item, tenant_id)
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[route], affected=1)
    return result

@router.put("/updateAll/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROUTE])
@inject
async def updateAll(
    request: Request,
    query: QueryArgs = query_param(),
    item: UpdateAllRoute = Body(),
    route_service: RouteService = Depends(
        Provide[AppContainer.route_package.route_service])
):
    tenant_id = request.user.tenant_id
    count = len([sec for frst in query.where for sec in frst.value])  # type: ignore  
    update_count = await route_service.update_all(query, item, tenant_id)
    is_success = True if update_count == count else False  
    result = ActionResult(success=is_success, affected=update_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/{route_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROUTE])
@inject
async def delete(
    request: Request,
    route_id: str,
    route_service: RouteService = Depends(
        Provide[AppContainer.route_package.route_service])
):
    tenant_id = request.user.tenant_id
    is_success = await route_service.delete(route_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROUTE])
@inject
async def delete_by_ids(
    request: Request,
    route_ids: List[str],
    route_service: RouteService = Depends(
        Provide[AppContainer.route_package.route_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await route_service.delete_by_ids(route_ids, tenant_id)
    is_success = True if deleted_count == len(route_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_ROUTE])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    route_service: RouteService = Depends(
        Provide[AppContainer.route_package.route_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await route_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
