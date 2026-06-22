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

from mapa.core.data.query_args import QueryArgs, Filter, FilterOp
from mapa.spatial.layer.layer_model import Layer
from mapa.spatial.layer.layer_service import LayerService
from mapa.spatial.layer_definition.layer_definition_service import LayerDefinitionService
from typing import Any
from mapa.spatial.models.merge_layer_model import MergeLayer

from mapa.spatial.connection.connection_service import ConnectionService

@router.get("/layer_full_info/{layer_id}", response_model=Any)
@authorize([ApiScopeType.QUERY_LAYER])
@inject
async def get_layer_full_info(
    request: Request,
    layer_id: str,
    config: Any = Depends(Provide[AppContainer.config]),
    layer_service: LayerService = Depends(
        Provide[AppContainer.layer_package.layer_service]),
    map_service: MapService = Depends(
        Provide[AppContainer.map_package.map_service]),
    layer_def_service: LayerDefinitionService = Depends(
        Provide[AppContainer.layer_package.layer_definition_service]),
    connection_service: ConnectionService = Depends(
        Provide[AppContainer.connection_package.connection_service])
):
    tenant_id = request.user.tenant_id
    query = QueryArgs(
        where=[Filter(field="id", op=FilterOp.EQUAL, value=layer_id)],
        expand=["connection"]
    )
    layers = await layer_service.find(query, tenant_id)
    layer = layers[0] if layers else None
    
    if not layer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
            
    # Fallback to fetch connection manually if expand=["connection"] failed
    if not layer.connection and layer.connection_id:
        conn_query = QueryArgs(
            where=[Filter(field="id", op=FilterOp.EQUAL, value=str(layer.connection_id))]
        )
        connection = await connection_service.find_one(conn_query, tenant_id)
        if connection:
            layer.connection = connection
            
    if layer.connection:
        gateway_params = await map_service.get_gateway_params(layer.connection, tenant_id)
        layer.layer_gateway_params = gateway_params
        
    ld_query = QueryArgs(
        where=[Filter(field="layer_id", op=FilterOp.EQUAL, value=layer_id)],
        expand=["definition", "layer_hooks"]
    )
    layer_def = await layer_def_service.find_one(ld_query, tenant_id)
    
    tenant = await map_service.get_tenant(tenant_id)
    tenant_name = tenant.name if tenant else "api"
    service_host = config["oidc"]["service_host"]
    
    definition = layer_def.definition if layer_def and hasattr(layer_def, "definition") else None
    
    layer_hooks_gateway_params = None
    if layer_def and hasattr(layer_def, "layer_hooks") and layer_def.layer_hooks:
        layer_hooks_gateway_params = await map_service.get_layer_hooks_gateway_params(layer_def.layer_hooks, tenant_id)

    merged_layer = MergeLayer(
        id=layer.id,
        map_layer_name=layer.name,
        order=1,
        layer_hooks=layer_def.layer_hooks if layer_def and hasattr(layer_def, "layer_hooks") else None,
        layer_hooks_gateway_params=layer_hooks_gateway_params,
        title=definition.title if definition else layer.title,
        default_extent=definition.default_extent if definition else layer.default_extent,
        max_scale=layer.max_scale,
        min_scale=layer.min_scale,
        opacity=layer.opacity,
        timer=layer.timer,
        data_type=layer.data_type,
        key_field=layer.key_field,
        type_name=layer.type_name,
        style_params=layer.style_params,
        field_params=layer.field_params,
        target_namespace=layer.target_namespace,
        name=layer.name,
        code=layer.code,
        description=layer.description,
        visible=layer.visible,
        connection_id=layer.connection_id,
        connection=layer.connection,
        geometry_field_param=layer.geometry_field_param,
        layer_gateway_params=layer.layer_gateway_params,
        is_attribute_panel=definition.is_attribute_panel if definition else None,
        tenant_name=tenant_name,
        service_host=service_host
    )
    
    merged_dict = merged_layer.model_dump(mode="json")
    if layer_def and hasattr(layer_def, "route_id"):
        merged_dict["route_id"] = str(layer_def.route_id) if layer_def.route_id else None

    return merged_dict
