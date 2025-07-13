import asyncio
import random
from typing import Any, Dict
from uuid import uuid4

import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.route.route_service import RouteService
from mapa.spatial.bookmark.bookmark_model import (Bookmark, UpdateAllBookmark,
                                                 UpdateBookmark)
from mapa.spatial.constant import MapWidgetType, SridTypes
from mapa.spatial.map.map_entity import MapEntity
from mapa.spatial.map.map_model import CreateMap, Types
from mapa.spatial.map.map_service import MapService
from mapa.spatial.map_layer.map_layer_entity import MapLayerEntity
from mapa.spatial.namespace.namespace_model import CreateNamespace
from mapa.spatial.namespace.namespace_service import NamespaceService
from mapa.spatial.bookmark.bookmark_service import BookmarkService
from mapa.spatial.map_base_layer.map_base_layer_service import MapBaseLayerService
from mapa.spatial.reference.reference_service import ReferenceService
from nanoid import generate

from .conftest import GatewayFixture, ManageFixture, SpatialFixture
from .data import generate_bookmark, tenant_id


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

    route_service = RouteService(async_db_gateway)

    fixture_manage = ManageFixture()
    initialized_manage = await fixture_manage.create_test_data()
    assert initialized_manage is True
    async_db_manage = fixture_manage.create_db_instance(
        fixture_manage.db_url_async)


    reference_service= ReferenceService(async_db)
    bookmark_service= BookmarkService(async_db)
    map_base_layer_service= MapBaseLayerService(async_db)
    return {
        "namespace_service": NamespaceService(async_db),
        "bookmark_service": bookmark_service,
        "map_service": MapService(async_db, route_service,reference_service,bookmark_service,map_base_layer_service),
    }



@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    map_service: MapService = services["map_service"]
    namespace_service: NamespaceService = services["namespace_service"]
    bookmark_service: BookmarkService = services["bookmark_service"]

    assert bookmark_service is not None
    assert namespace_service is not None
    assert map_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """BookmarkService Crud Test"""
    services = await create_services(fixture)
    map_service: MapService = services["map_service"]
    bookmark_service: BookmarkService = services["bookmark_service"]
    namespace_service: NamespaceService = services["namespace_service"]

    assert namespace_service is not None
    assert map_service is not None
    assert bookmark_service is not None

    # User eklenir.
    # user_data = await user_service.create(CreateUser(
    #     name=f"Test_user_bookmark", surname="Test_user_bookmark",
    #     email=f"test__bookmark@gmail.com", password="1123124",
    #     subject_id="1123123", phone="1"), str(tenant_id))
    # assert user_data is not None

    # Namespace Yeni 1 adet kayıt oluşturulur.
    namespace_data = await namespace_service.create(CreateNamespace(
        name="namespace_fk_bookmark"+generate(size=4),
        title="_bookmark_fk_Test"+generate(size=32),
        description="_bookmark_fk_Test"+generate(size=64),
        identifier="https://namespace_identifier_bookmark_"+generate(size=4)), str(tenant_id))
    assert namespace_data is not None

    # map eklenir
    map_data = await map_service.create(CreateMap(
        namespace_id=namespace_data.id,
        name="bookmark_map_test"+generate(size=4),
        title="bookmark_map_test_title",
        description="bookmark_map_test_desc",
        initial_extent="97.65656917606952;37.86541500399325;75.1803520939344;19.7160900653360" +
        str(random.randint(0, 10)),
        full_extent="46.333723794096386;46.29575588844355;23.85750671196024;30.02581711044706" +
        str(random.randint(0, 10)),
        srid=SridTypes.EPSG_3857,
        zoom=18,
        widget_types=[Types(key=MapWidgetType.AttributeTable), Types(
            key=MapWidgetType.Bookmark), Types(key=MapWidgetType.Info)]
    ), tenant_id=tenant_id)

    # Boş bir sorgulama yapılır
    empty_item = await bookmark_service.get(str(user_data.id), str(uuid4()), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (bookmark_service.create(str(user_data.id), generate_bookmark(user_data.id, map_data.id), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await bookmark_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: Bookmark = items[0]

    updated_first_item = await bookmark_service.update(first_item.id, UpdateBookmark(
        thumbnail=test_value, name=first_item.name, location=first_item.location,
        map_id=first_item.map_id, user_id=first_item.user_id
    ), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.thumbnail == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="thumbnail", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await bookmark_service.update_all(query_args_update, UpdateAllBookmark(
        thumbnail=test_value_2
    ), tenant_id=tenant_id)
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await bookmark_service.get(str(user_data.id), str(first_item.id), tenant_id=tenant_id)
    assert updated_first_item.thumbnail == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await bookmark_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await bookmark_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="thumbnail", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await bookmark_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await bookmark_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0

    # map silinir
    map_data = await map_service.delete(map_data.id, str(tenant_id))
    assert map_data is not None

    # namespace silinir
    namespace_data = await namespace_service.delete(namespace_data.id, str(tenant_id))
    assert namespace_data is not None

    # # user silinir
    # user_data = await user_service.delete(user_data.id, str(tenant_id))
    # assert user_data is not None
