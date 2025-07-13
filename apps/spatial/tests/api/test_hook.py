import asyncio
from typing import Any, Dict, List
from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.hook.hook_model import (CreateHook, Hook, UpdateAllHook,
                                         UpdateHook)
from mapa.spatial.hook.hook_service import HookService

from .conftest import SpatialFixture
from .data import generate_hook_list, tenant_id


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    return {
        "hook_service": HookService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)
    hook_service: HookService = services["hook_service"]

    assert hook_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: SpatialFixture):
    """HookService Crud Test"""
    services = await create_services(fixture)
    hook_service: HookService = services["hook_service"]

    assert hook_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await hook_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    hooks: List[CreateHook] = generate_hook_list()
    el_count = len(hooks)
    task_list = (hook_service.create(hooks[i], tenant_id=tenant_id)
                 for i in range(0, el_count))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await hook_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
            str(item.id) for item in items])
    ], order={
        "type": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: Hook = items[0]

    updated_first_item = await hook_service.update(first_item.id, UpdateHook(
        type=first_item.type, operation_type=first_item.operation_type, description=test_value), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.description == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="description", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik_test"
    updated_el_count = await hook_service.update_all(query_args_update, UpdateAllHook(
        description=test_value_2
    ), tenant_id=tenant_id)
    assert updated_el_count > 0

    # ilk elemanı sorgulanır
    updated_first_item = await hook_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.description == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await hook_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await hook_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="description", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await hook_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await hook_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0
