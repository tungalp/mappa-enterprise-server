import asyncio
import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.context_var.context_var_model import ConvextVar, UpdateAllConvextVar, UpdateConvextVar
from mapa.gateway.context_var.context_var_service import ContextVarService
from .conftest import GatewayFixture, generate_context_var, generate_context_var2,tenant_id
from uuid import uuid4
from typing import Any, Dict


async def create_services(fixture: GatewayFixture) -> Dict[str, Any]:
    """"Create All Services"""
    
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    context_var_service = ContextVarService(async_db)
    return {
        "context_var_service": context_var_service,
    }


@pytest.mark.asyncio
async def test_create_service(fixture: GatewayFixture):
    """Service"""
    services = await create_services(fixture)
    context_var_service: ContextVarService = services["context_var_service"]
    assert context_var_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: GatewayFixture):
    """GatewayApiService Crud Test"""
    services = await create_services(fixture)
    context_var_service: ContextVarService = services["context_var_service"]

    assert context_var_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await context_var_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (context_var_service.create(generate_context_var(), tenant_id=tenant_id)
                 for i in range(1, int(el_count / 2) + 1))
    task_list2 = (context_var_service.create(generate_context_var2(), tenant_id=tenant_id)
                for i in range(1, int(el_count / 2) + 1))
    all_tasks = (*task_list,  *task_list2)
    items = await asyncio.gather(*all_tasks)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await context_var_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "key": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: ConvextVar = items[0]

    updated_first_item = await context_var_service.update(first_item.id, UpdateConvextVar(
        key=first_item.key, value=test_value), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.value == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="key", op=FilterOp.LIKE, value="key_%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await context_var_service.update_all(query_args_update, UpdateAllConvextVar(
        value=test_value_2
    ), tenant_id=tenant_id)
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await context_var_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.value == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await context_var_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await context_var_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs()
    deleted_row_count = await context_var_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await context_var_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0
