import asyncio
import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.user.user_model import CreateUser, UpdateAllUser, UpdateUser, User
from mapa.manage.user.user_service import UserService
from mapa.manage.api.api_service import ApiService
from .conftest import SsoFixture


async def create_service(fixture: SsoFixture) -> UserService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)     
    organization_client_service = OrganizationClientService(async_db)
    organization_service = OrganizationService(async_db,organization_client_service)
   
    return UserService(async_db, api_service,organization_service)


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    service: UserService = await create_service(fixture)

    assert service is not None


@pytest.mark.asyncio
async def test_crud_user(fixture: SsoFixture):
    """Service"""
    service: UserService = await create_service(fixture)
    assert service is not None

    # Boş bir sorgulama yapılır
    empty_item = await service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(fixture.tenant_id))
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (service.create(CreateUser(
        subject_id=f"Subject_{i}", name=f"Test_{i}", surname="Test", email=f"test_{i}@gmail.com", password=f"p@ssw0rd{i}"), tenant_id=str(fixture.tenant_id))
        for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), tenant_id=str(fixture.tenant_id))
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_X"
    first_item = items[0]
    updated_user = UpdateUser(
        name=test_value
    )
    updated_first_item = await service.update(first_item.id, updated_user, tenant_id=str(fixture.tenant_id))
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="surname", op=FilterOp.EQUAL, value="Test")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await service.update_all(query_args_update, UpdateAllUser(
        surname=test_value_2
    ), tenant_id=str(fixture.tenant_id))
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await service.get(first_item.id, str(fixture.tenant_id))
    assert updated_first_item.surname == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await service.delete(updated_first_item.id, str(fixture.tenant_id))
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await service.delete_by_ids(last_item_ids, str(fixture.tenant_id))
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="surname", op=FilterOp.EQUAL, value=test_value_2)
    ])
    remaing_users = await service.find(query_args_delete, str(fixture.tenant_id))
    deleted_row_count = await service.delete_by_ids([user.id for user in remaing_users], str(fixture.tenant_id))
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await service.find(query_args_delete, tenant_id=str(fixture.tenant_id))
    assert len(deleted_rows) == 0
