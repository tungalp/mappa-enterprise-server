import asyncio
from typing import Any, Dict
from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.namespace.namespace_model import (Namespace,
                                                   UpdateAllNamespace,
                                                   UpdateNamespace)
from mapa.spatial.namespace.namespace_service import NamespaceService
from nanoid import generate

from .conftest import SpatialFixture
from .data import generate_namespace, tenant_id


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    return {
        "namespace_service": NamespaceService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    namespace_service: NamespaceService = services["namespace_service"]

    assert namespace_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """NamespaceService Crud Test"""
    services = await create_services(fixture)
    namespace_service: NamespaceService = services["namespace_service"]

    assert namespace_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await namespace_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (namespace_service.create(generate_namespace(), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await namespace_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: Namespace = items[0]

    updated_first_item = await namespace_service.update(first_item.id, UpdateNamespace(
        name=test_value, identifier="https://namespace_identifier_" +
        generate(size=4)
    ), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="description", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik_test"
    updated_el_count = await namespace_service.update_all(query_args_update, UpdateAllNamespace(
        description=test_value_2
    ), tenant_id=tenant_id)
    assert updated_el_count > 0

    # ilk elemanı sorgulanır
    updated_first_item = await namespace_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.description == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await namespace_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await namespace_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="description", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await namespace_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await namespace_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0
