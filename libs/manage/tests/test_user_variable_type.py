import asyncio
from typing import Any, Dict
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.user_variable_type.user_variable_type_model import CreateUserVariableType, UpdateAllUserVariableType, UpdateUserVariableType
from mapa.manage.user_variable_type.user_variable_type_service import UserVariableTypeService
from .conftest import ManageFixture


async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    return {
        "user_variable_type_service": UserVariableTypeService(async_db),  
    }


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    assert services["user_variable_type_service"] is not None


@pytest.mark.asyncio
async def test_crud_user_variable_type(fixture: ManageFixture):
    """Service"""

    services = await create_services(fixture)
    assert services["user_variable_type_service"] is not None

    user_variable_type_service: UserVariableTypeService = services["user_variable_type_service"]
    assert user_variable_type_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await user_variable_type_service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(fixture.tenant_id))
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (user_variable_type_service.create(CreateUserVariableType(
        name=f"Test_{i}", description=f"Test_desc_{i}"), tenant_id=str(fixture.tenant_id))
        for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await user_variable_type_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), tenant_id=str(fixture.tenant_id))
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_X"
    first_item = items[0]

    # birinci elamanın bilgisini döner
    selected_one = await user_variable_type_service.get_by_user_variable_type_id(first_item.id, tenant_id=str(fixture.tenant_id))
    assert selected_one.id == first_item.id

    updated_first_item = await user_variable_type_service.update(first_item.id, UpdateUserVariableType(
        name=test_value, description=test_value
    ), tenant_id=str(fixture.tenant_id))
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="description", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await user_variable_type_service.update_all(query_args_update, UpdateAllUserVariableType(
        description=test_value_2
    ), tenant_id=str(fixture.tenant_id))
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await user_variable_type_service.get(first_item.id, tenant_id=str(fixture.tenant_id))
    assert updated_first_item.description == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await user_variable_type_service.delete(updated_first_item.id, str(fixture.tenant_id))
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await user_variable_type_service.delete_by_ids(last_item_ids, str(fixture.tenant_id))
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="description", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await user_variable_type_service.delete_all(query_args_delete, tenant_id=str(fixture.tenant_id))
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await user_variable_type_service.find(query_args_delete, tenant_id=str(fixture.tenant_id))
    assert len(deleted_rows) == 0
