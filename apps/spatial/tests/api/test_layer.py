import asyncio
from typing import Any, Dict
from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService
from mapa.gateway.route.route_service import RouteService
from mapa.spatial.connection.connection_service import ConnectionService
from mapa.spatial.definition.definition_service import DefinitionService
from mapa.spatial.layer.layer_model import Layer, UpdateAllLayer, UpdateLayer
from mapa.spatial.layer.layer_service import LayerService
from mapa.spatial.layer_definition.layer_definition_entity import \
    LayerDefinitionEntity
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService
from mapa.spatial.layer_hook.layer_hook_entity import LayerHookEntity
from mapa.spatial.layer_hook.layer_hook_service import LayerHookService

from .conftest import SpatialFixture
from .data import (generate_connection, generate_gateway_api, generate_layer,
                   generate_route, tenant_id)


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    layer_definition_service = LayerDefinitionService(async_db)
    layer_hook_service= LayerHookService(async_db)
    return {
        "definition_service": DefinitionService(async_db,layer_definition_service,layer_hook_service),
        "gateway_api_service": GatewayApiService(async_db),
        "route_service": RouteService(async_db),
        "connection_service": ConnectionService(async_db),
        "layer_service": LayerService(async_db, layer_definition_service),
        "layer_definition_service": LayerDefinitionService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    layer_service: LayerService = services["layer_service"]
    connection_service: ConnectionService = services["connection_service"]
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    route_service: RouteService = services["route_service"]
    layer_definition_service: LayerDefinitionService = services["layer_definition_service"]
    definition_service: DefinitionService = services["definition_service"]

    assert definition_service is not None
    assert layer_definition_service is not None
    assert gateway_api_service is not None
    assert route_service is not None
    assert connection_service is not None
    assert layer_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """LayerService Crud Test"""
    services = await create_services(fixture)
    layer_service: LayerService = services["layer_service"]
    connection_service: ConnectionService = services["connection_service"]
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    route_service: RouteService = services["route_service"]
    layer_definition_service: LayerDefinitionService = services["layer_definition_service"]
    definition_service: DefinitionService = services["definition_service"]

    assert definition_service is not None
    assert layer_definition_service is not None
    assert gateway_api_service is not None
    assert route_service is not None
    assert connection_service is not None
    assert layer_service is not None

    # Api oluşturulur
    gateway_api_data = await gateway_api_service.create(generate_gateway_api(), tenant_id)
    assert gateway_api_data is not None

    # Route oluşturulur
    route_data = await route_service.create(generate_route(gateway_api_data.id), tenant_id)
    assert route_data is not None

    # Connection Yeni 1 adet kayıt oluşturulur.
    connection_data = await connection_service.create(generate_connection(route_data.id), str(tenant_id))
    assert connection_data is not None

    # Boş bir sorgulama yapılır
    empty_item = await layer_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (layer_service.create(generate_layer(connection_data.id), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await layer_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: Layer = items[0]

    updated_first_item = await layer_service.update(first_item.id, UpdateLayer(
        name=test_value, connection_id=first_item.connection_id,
        default_extent=first_item.default_extent,
        max_scale=first_item.max_scale,
        min_scale=first_item.min_scale,
        opacity=first_item.opacity,
        timer=first_item.timer,
        visible=first_item.visible,
        field_params=first_item.field_params,
        geometry_field_param=first_item.geometry_field_param,
        style_params=first_item.style_params,
        data_type=first_item.data_type,
        key_field=first_item.key_field,
        type_name=first_item.type_name,
        target_namespace=first_item.target_namespace,
    ), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="description", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await layer_service.update_all(query_args_update, UpdateAllLayer(
        description=test_value_2
    ), tenant_id=tenant_id)
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await layer_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.description == test_value_2

    # layer silinmeden önce layer def bilgisi bulunur ve silinir
    layer_def_query_args = QueryArgs(where=[
        Filter(field="definition_id", op=FilterOp.NULL, value = uuid4())
    ])

    layer_definition_data = await layer_definition_service.find(layer_def_query_args, str(tenant_id))
    assert layer_definition_data is not None

    layer_def_ids = [cust.id for cust in layer_definition_data]
    first_row_deleted = await layer_definition_service.delete_by_ids(layer_def_ids, tenant_id)
    assert first_row_deleted == len(layer_definition_data)

    # ilk kayıt silinir
    first_row_deleted = await layer_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await layer_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="description", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await layer_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await layer_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0

    # Connection silinir
    connection_data = await connection_service.delete(connection_data.id, str(tenant_id))
    assert connection_data is not None

    # Route silinir
    route_data = await route_service.delete(route_data.id, tenant_id)
    assert route_data is not None

    # Api silinir
    gateway_api_data = await gateway_api_service.delete(gateway_api_data.id, tenant_id)
    assert gateway_api_data is not None
