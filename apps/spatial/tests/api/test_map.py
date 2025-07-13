import asyncio
from typing import Any, Dict
from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.route.route_service import RouteService
from mapa.spatial.map.map_model import Map, UpdateAllMap, UpdateMap
from mapa.spatial.map.map_service import MapService
from mapa.spatial.namespace.namespace_model import CreateNamespace
from mapa.spatial.namespace.namespace_service import NamespaceService
from mapa.spatial.bookmark.bookmark_service import BookmarkService
from mapa.spatial.map_base_layer.map_base_layer_service import MapBaseLayerService
from mapa.spatial.reference.reference_service import ReferenceService
from nanoid import generate

from .conftest import GatewayFixture, SpatialFixture
from .data import generate_map, tenant_id


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    fixture_gateway = GatewayFixture()
    initialized_gateway = await fixture_gateway.create_test_data()
    assert initialized_gateway is True
    async_db_gateway = fixture_gateway.create_db_instance(
        fixture_gateway.db_url_async)
    
    
    reference_service= ReferenceService(async_db)
    bookmark_service= BookmarkService(async_db)
    map_base_layer_service= MapBaseLayerService(async_db)

    route_service = RouteService(async_db_gateway)
    return {
        "namespace_service": NamespaceService(async_db),
        "map_service": MapService(async_db, route_service,reference_service,bookmark_service,map_base_layer_service),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    map_service: MapService = services["map_service"]
    namespace_service: NamespaceService = services["namespace_service"]

    assert namespace_service is not None
    assert map_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """MapService Crud Test"""
    services = await create_services(fixture)
    map_service: MapService = services["map_service"]
    namespace_service: NamespaceService = services["namespace_service"]

    assert namespace_service is not None
    assert map_service is not None

    # Namespace Yeni 1 adet kayıt oluşturulur.
    namespace_data = await namespace_service.create(CreateNamespace(
        name="namespace_fk_"+generate(size=4),
        title="fk_Test"+generate(size=32),
        description="fk_Test"+generate(size=64),
        identifier="https://namespace_identifier_"+generate(size=4)), str(tenant_id))
    assert namespace_data is not None

    # Boş bir sorgulama yapılır
    empty_item = await map_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (map_service.create(generate_map(namespace_data.id), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await map_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: Map = items[0]

    updated_first_item = await map_service.update(first_item.id, UpdateMap(
        name=test_value, initial_extent=first_item.initial_extent, full_extent=first_item.full_extent, namespace_id=first_item.namespace_id,
        srid=first_item.srid,zoom=first_item.zoom
    ), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="description", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await map_service.update_all(query_args_update, UpdateAllMap(
        description=test_value_2,zoom=first_item.zoom
    ), tenant_id=tenant_id)
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await map_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.description == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await map_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await map_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="description", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await map_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await map_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0

    # namespace silinir
    namespace_data = await namespace_service.delete(namespace_data.id, str(tenant_id))
    assert namespace_data is not None
