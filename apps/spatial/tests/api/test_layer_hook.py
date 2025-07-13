import asyncio
from typing import Any, Dict
from uuid import uuid4

import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.constant import ApiTypes, MethodTypes
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService
from mapa.gateway.integration.integration_service import IntegrationService
from mapa.gateway.route.route_model import CreateRoute
from mapa.gateway.route.route_service import RouteService
from mapa.spatial.connection.connection_service import ConnectionService
from mapa.spatial.constant import HookOperationType
from mapa.spatial.layer.layer_service import LayerService
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService
from mapa.spatial.layer_hook.layer_hook_model import LayerHook
from mapa.spatial.layer_hook.layer_hook_service import LayerHookService
from mapa.spatial.map.map_service import MapService
from mapa.spatial.namespace.namespace_model import CreateNamespace
from mapa.spatial.namespace.namespace_service import NamespaceService
from mapa.spatial.bookmark.bookmark_service import BookmarkService
from mapa.spatial.map_base_layer.map_base_layer_service import MapBaseLayerService
from mapa.spatial.reference.reference_service import ReferenceService
from mapa.gateway.connection_info.connection_info_service import \
    ConnectionInfoService
from nanoid import generate

from .conftest import GatewayFixture, SpatialFixture
from .data import (generate_connection, generate_gateway_api, generate_layer,
                   generate_layer_hook, generate_map, generate_route,
                   tenant_id)


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)

    fixture_gateway = GatewayFixture()
    initialized_gateway = await fixture_gateway.create_test_data()
    assert initialized_gateway is True
    async_db_gateway = fixture_gateway.create_db_instance(
        fixture_gateway.db_url_async)
    
    connection_info_service = ConnectionInfoService(async_db)
    gateway_api_service = GatewayApiService(async_db_gateway)
    route_service = RouteService(async_db_gateway)
    integration_service = IntegrationService(async_db_gateway,route_service,connection_info_service)

    layer_definition_service = LayerDefinitionService(async_db)
    reference_service= ReferenceService(async_db)
    bookmark_service= BookmarkService(async_db)
    map_base_layer_service= MapBaseLayerService(async_db)
    return {
        "layer_hook_service": LayerHookService(async_db),

        "gateway_api_service": gateway_api_service,
        "route_service": route_service,
        "integration_service": integration_service,

        "namespace_service": NamespaceService(async_db),
        "connection_service": ConnectionService(async_db),
        "layer_service": LayerService(async_db, layer_definition_service),
        "layer_definition_service": LayerDefinitionService(async_db),
        "map_service": MapService(async_db, route_service,reference_service,bookmark_service,map_base_layer_service),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    layer_hook_service: LayerHookService = services["layer_hook_service"]
    map_service: MapService = services["map_service"]
    namespace_service: NamespaceService = services["namespace_service"]
    layer_service: LayerService = services["layer_service"]
    connection_service: ConnectionService = services["connection_service"]
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    route_service: RouteService = services["route_service"]
    layer_definition_service: LayerDefinitionService = services["layer_definition_service"]

    assert layer_hook_service is not None
    assert layer_definition_service is not None
    assert gateway_api_service is not None
    assert route_service is not None
    assert connection_service is not None
    assert layer_service is not None
    assert namespace_service is not None
    assert map_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """LayerHookService Crud Test"""
    services = await create_services(fixture)
    layer_hook_service: LayerHookService = services["layer_hook_service"]
    map_service: MapService = services["map_service"]
    namespace_service: NamespaceService = services["namespace_service"]
    layer_service: LayerService = services["layer_service"]
    connection_service: ConnectionService = services["connection_service"]
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    route_service: RouteService = services["route_service"]
    layer_definition_service: LayerDefinitionService = services["layer_definition_service"]

    assert layer_hook_service is not None
    assert layer_definition_service is not None
    assert gateway_api_service is not None
    assert route_service is not None
    assert connection_service is not None
    assert layer_service is not None
    assert namespace_service is not None
    assert map_service is not None

    # Hook Api oluşturulur
    hook_api_data = await gateway_api_service.create(CreateGatewayApi(
        name="hook Api",
        type=ApiTypes.HTTP,
        path="hookapi",
        identifier="https://api.hookapi",
    ), tenant_id=tenant_id)

    # Hook Route oluşturulur
    hook_route = await route_service.create(CreateRoute(description="hook route",
                                                        path="hookrouteget",
                                                        method_type=MethodTypes.GET,
                                                        gateway_api_id=hook_api_data.id), tenant_id=tenant_id)

    # Api oluşturulur
    gateway_api_data = await gateway_api_service.create(generate_gateway_api(), tenant_id)
    assert gateway_api_data is not None

    # Route oluşturulur
    route_data = await route_service.create(generate_route(gateway_api_data.id), tenant_id)
    assert route_data is not None

    # Connection Yeni 1 adet kayıt oluşturulur.
    connection_data = await connection_service.create(generate_connection(route_data.id), str(tenant_id))
    assert connection_data is not None

    # layer eklenir
    layer_data = await layer_service.create(generate_layer(connection_data.id), str(tenant_id))
    assert layer_data is not None

    # namespace eklenir
    namespace_data = await namespace_service.create(CreateNamespace(
        name="namespace_test_ns"+generate(size=4),
        title="nsTest"+generate(size=4),
        description="nsTest"+generate(size=4),
        identifier="nshttps://namespace_identifier_"+generate(size=4)), str(tenant_id))
    assert namespace_data is not None

    # map eklenir
    map_data = await map_service.create(generate_map(namespace_data.id), str(tenant_id))
    assert map_data is not None

    # eklenen layer'a göre layer def. sorgulanır

    layer_def_query_args = QueryArgs(where=[
        Filter(field="layer_id", op=FilterOp.EQUAL, value=layer_data.id)
    ])

    layer_definition_data = await layer_definition_service.find(layer_def_query_args, str(tenant_id))
    assert layer_definition_data is not None

    # Boş bir sorgulama yapılır
    empty_item = await layer_hook_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 1
    task_list = (layer_hook_service.create(generate_layer_hook(hook_route.id, layer_definition_data[0].id, hook_operation_type=HookOperationType.GET), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await layer_hook_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "hook_operation_type": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    # test_value = "Test_XXX"
    first_item: LayerHook = items[0]

    # updated_first_item = await layer_hook_service.update(first_item.id, UpdateLayerHook(
    #     name=test_value, order=first_item.order, map_id=first_item.map_id, layer_definition_id=first_item.layer_definition_id
    # ), tenant_id=tenant_id)
    # assert updated_first_item.name == test_value

    # ilk kayıt silinir
    first_row_deleted = await layer_hook_service.delete(first_item.id, tenant_id)
    assert first_row_deleted is True

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="hook_operation_type",
               op=FilterOp.NOT_NULL, value="Test%")
    ])
    deleted_row_count = await layer_hook_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 1

    # Silinenler sorgulanır
    deleted_rows = await layer_hook_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0

    # layer def silinir
    layer_definition_data = await layer_definition_service.delete(layer_definition_data[0].id, str(tenant_id))
    assert layer_definition_data is not None

    # layer silinir
    layer_data = await layer_service.delete(layer_data.id, str(tenant_id))
    assert layer_data is not None

    # map silinir
    map_data = await map_service.delete(map_data.id, str(tenant_id))
    assert map_data is not None

    # namespace silinir
    namespace_data = await namespace_service.delete(namespace_data.id, str(tenant_id))
    assert namespace_data is not None

    # Connection silinir
    connection_data = await connection_service.delete(connection_data.id, str(tenant_id))
    assert connection_data is not None

    # Route silinir
    route_data = await route_service.delete(route_data.id, tenant_id)
    assert route_data is not None

    # Api silinir
    gateway_api_data = await gateway_api_service.delete(gateway_api_data.id, tenant_id)
    assert gateway_api_data is not None

    # Hook Route silinir
    hook_route = await route_service.delete(hook_route.id, tenant_id)
    assert hook_route is not None

    # Hook Api silinir
    hook_api_data = await gateway_api_service.delete(hook_api_data.id, tenant_id)
    assert hook_api_data is not None
