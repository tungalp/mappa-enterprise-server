import asyncio
from typing import Any, Dict
from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.gateway_api.gateway_api_model import (CreateGatewayApi,
                                                       GatewayApi)
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService
from mapa.gateway.route.route_model import CreateRoute, Route
from mapa.gateway.route.route_service import RouteService
from mapa.spatial.connection.connection_model import (Connection,
                                                     UpdateAllConnection,
                                                     UpdateConnection)
from mapa.spatial.connection.connection_service import ConnectionService

from .conftest import SpatialFixture
from .data import (generate_connection, generate_gateway_api, generate_route,
                   tenant_id)


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    return {
        "gateway_api_service": GatewayApiService(async_db),
        "route_service": RouteService(async_db),
        "connection_service": ConnectionService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    connection_service: ConnectionService = services["connection_service"]
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    route_service: RouteService = services["route_service"]

    assert gateway_api_service is not None
    assert route_service is not None
    assert connection_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """ConnectionService Crud Test"""
    services = await create_services(fixture)
    connection_service: ConnectionService = services["connection_service"]
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    route_service: RouteService = services["route_service"]

    assert gateway_api_service is not None
    assert route_service is not None
    assert connection_service is not None

    # Api oluşturulur
    create_gateway_api: CreateGatewayApi = generate_gateway_api()
    gateway_api: GatewayApi = await gateway_api_service.create(create_gateway_api, tenant_id)
    assert gateway_api is not None

    # Route oluşturulur
    create_route: CreateRoute = generate_route(gateway_api.id)
    route: Route = await route_service.create(create_route, tenant_id)
    assert route is not None

    # Boş bir sorgulama yapılır
    empty_item = await connection_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (connection_service.create(generate_connection(route.id), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await connection_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: Connection = items[0]

    updated_first_item = await connection_service.update(first_item.id, UpdateConnection(
        name=test_value, route_params=first_item.route_params,type=first_item.type 
    ), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="description", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await connection_service.update_all(query_args_update, UpdateAllConnection(
        description=test_value_2
    ), tenant_id=tenant_id)
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await connection_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.description == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await connection_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await connection_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="description", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await connection_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await connection_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0
