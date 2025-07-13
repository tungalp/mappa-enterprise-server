import asyncio
import random
from typing import Any, Dict
from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.route.route_service import RouteService
from mapa.spatial.base_layer.base_layer_model import (BaseLayerConnection,
                                                     CreateBaseLayer)
from mapa.spatial.base_layer.base_layer_service import BaseLayerService
from mapa.spatial.constant import BaseLayerTypes, MapWidgetType, SridTypes
from mapa.spatial.map.map_model import CreateMap, Types
from mapa.spatial.map.map_service import MapService
from mapa.spatial.namespace.namespace_model import CreateNamespace
from mapa.spatial.namespace.namespace_service import NamespaceService
from mapa.spatial.bookmark.bookmark_service import BookmarkService
from mapa.spatial.map_base_layer.map_base_layer_service import MapBaseLayerService
from mapa.spatial.reference.reference_service import ReferenceService

from .conftest import GatewayFixture, SpatialFixture
from .data import generate_map_base_layer, map_base_layer_select, tenant_id


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

    route_service = RouteService(async_db_gateway)
    
    reference_service= ReferenceService(async_db)
    bookmark_service= BookmarkService(async_db)
    map_base_layer_service= MapBaseLayerService(async_db)
    return {
        "map_base_layer_service": map_base_layer_service,
        "base_layer_service": BaseLayerService(async_db),
        "namespace_service": NamespaceService(async_db),
        "map_service": MapService(async_db, route_service,reference_service,bookmark_service,map_base_layer_service),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    base_layer_service: BaseLayerService = services["base_layer_service"]
    map_base_layer_service: MapBaseLayerService = services["map_base_layer_service"]
    map_service: MapService = services["map_service"]
    namespace_service: NamespaceService = services["namespace_service"]

    assert namespace_service is not None
    assert map_service is not None
    assert map_base_layer_service is not None
    assert base_layer_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """BaseLayerService Crud Test"""
    services = await create_services(fixture)
    base_layer_service: BaseLayerService = services["base_layer_service"]
    map_base_layer_service: MapBaseLayerService = services["map_base_layer_service"]
    map_service: MapService = services["map_service"]
    namespace_service: NamespaceService = services["namespace_service"]

    assert namespace_service is not None
    assert map_service is not None
    assert map_base_layer_service is not None
    assert base_layer_service is not None

    # base-layer eklenir
    base_layer_data = await base_layer_service.create(CreateBaseLayer(
        type=BaseLayerTypes.WebMapService, connection=BaseLayerConnection(name='test__', thumbnail="base64", tiles=['https://mt0.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                                                    'https://mt1.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                                                    'https://mt2.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                                                    'https://mt3.google.com/vt/lyrs=y&z={z}&x={x}&y={y}'], tile_size=256)
    ), tenant_id=tenant_id)
    assert base_layer_data is not None

    # namespace eklenir
    namespace_data = await namespace_service.create(CreateNamespace(
        name="info_namespace",
        title="map testi için",
        description="map testi için",
        identifier="https://namespace_identifier_map_testi"), tenant_id=tenant_id)
    assert namespace_data is not None

    # map eklenir
    map_data = await map_service.create(CreateMap(
        namespace_id=namespace_data.id,
        name="map_test",
        title="map_test_title",
        description="map_test_desc",
        initial_extent="97.65656917606952;37.86541500399325;75.1803520939344;19.7160900653360" +
        str(random.randint(0, 10)),
        full_extent="46.333723794096386;46.29575588844355;23.85750671196024;30.02581711044706" +
        str(random.randint(0, 10)),
        srid=SridTypes.EPSG_3857,
        zoom=12,
        widget_types=[Types(key=MapWidgetType.AttributeTable), Types(
            key=MapWidgetType.Bookmark), Types(key=MapWidgetType.Info)]
    ), tenant_id=tenant_id)
    assert map_data is not None

    # Boş bir sorgulama yapılır
    empty_item = await map_base_layer_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # map - base - layer eklenir
    map_base_layer_data = map_base_layer_service.create(
        generate_map_base_layer(map_data.id, base_layer_data.id), tenant_id=tenant_id)
    assert map_base_layer_data is not None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 1
    task_list = (map_base_layer_service.create(generate_map_base_layer(map_data.id, base_layer_data.id), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await map_base_layer_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "order": "desc"
    },
        select=map_base_layer_select
    ), tenant_id=tenant_id)
    assert len(selected_items) == len(items)

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await map_base_layer_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 1

    # base - layer silinir
    base_layer_data = await base_layer_service.delete(base_layer_data.id, str(tenant_id))
    assert base_layer_data is not None

    # map silinir
    map_data = await map_service.delete(map_data.id, str(tenant_id))
    assert map_data is not None

    # namespace silinir
    namespace_data = await namespace_service.delete(namespace_data.id, str(tenant_id))
    assert namespace_data is not None
