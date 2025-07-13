from typing import Any, Dict, List
from uuid import uuid4

from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.bookmark.bookmark_model import Bookmark
from mapa.spatial.constant import ApiScopeType
from mapa.spatial.map.map_model import CreateMap, Map, UpdateMap
from mapa.spatial.map.map_service import MapService
from mapa.spatial.map_base_layer.map_base_layer_model import MapBaseLayer

from mapa.spatial.reference.reference_model import Reference
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer

router = APIRouter()


@router.get("/map/map_info", response_model=PagingResult[Map])
@inject
async def map_info(
    request: Request,
    query: QueryArgs = query_param(),
    config: Any = Depends(Provide[AppContainer.config]),
    map_service: MapService = Depends(
        Provide[AppContainer.map_package.map_service])
):
    
    tenant_id_filter = [x for x in query.where if x.field == 'tenant_id' and x.op==FilterOp.EQUAL] # type: ignore
    if tenant_id_filter is None or len(tenant_id_filter) == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str('Tenant_id filter must be singular and one'))    
  
    tenant_id = str(tenant_id_filter[0].value) # type: ignore
    user_id = request.user.sub
    maps: PagingResult[Map] = await map_service.paging(
        query, tenant_id)
   
    if len(maps.items) > 0:
        maps.items = await map_service.get_map_full_info(maps.items, config["oidc"]["service_host"], tenant_id, user_id)

    return maps


@router.get("/{map_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_MAP])
@inject
async def find(
    request: Request,
    map_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    map_service: MapService = Depends(
        Provide[AppContainer.map_package.map_service])):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    map = await map_service.get(map_id, tenant_id, field_list)
    if not map:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    return map


@router.get("/", response_model=PagingResult[Map])
@authorize([ApiScopeType.QUERY_MAP])
@inject
async def paging(
    request: Request,
    query: QueryArgs = query_param(),
    map_service: MapService = Depends(
        Provide[AppContainer.map_package.map_service])
):
    tenant_id = request.user.tenant_id
    maps: PagingResult[Map] = await map_service.paging(
        query, tenant_id)  # type: ignore
    return maps


@router.post("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP])
@inject
async def create(
    request: Request,
    items: List[CreateMap] = Body(),
    map_service: MapService = Depends(
        Provide[AppContainer.map_package.map_service])
):
    tenant_id = request.user.tenant_id
    maps = await map_service.create_all(items, tenant_id)
    result = ActionResult(success=True, items=maps)
    return result


@router.put("/{map_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP])
@inject
async def update(
    request: Request,
    map_id: str,
    item: UpdateMap = Body(),
    map_service: MapService = Depends(
        Provide[AppContainer.map_package.map_service])
):
    tenant_id = request.user.tenant_id
    map = await map_service.update(map_id, item, tenant_id)
    if not map:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=True, items=[map], affected=1)
    return result


@router.delete("/{map_id}", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP])
@inject
async def delete(
    request: Request,
    map_id: str,
    map_service: MapService = Depends(
        Provide[AppContainer.map_package.map_service])
):
    tenant_id = request.user.tenant_id
    is_success = await map_service.delete(map_id, tenant_id)
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP])
@inject
async def delete_by_ids(
    request: Request,
    map_ids: List[str],
    map_service: MapService = Depends(
        Provide[AppContainer.map_package.map_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await map_service.delete_by_ids(map_ids, tenant_id)
    is_success = True if deleted_count == len(map_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())


@router.delete("/", status_code=201, response_model=ActionResult)
@authorize([ApiScopeType.EDIT_MAP])
@inject
async def delete_all(
    request: Request,
    query: QueryArgs = query_param(),
    map_service: MapService = Depends(
        Provide[AppContainer.map_package.map_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await map_service.delete_all(query, tenant_id)
    result = ActionResult(success=True, affected=deleted_count)
    return JSONResponse(content=result.model_dump())
