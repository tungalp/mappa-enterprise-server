import asyncio
import uuid
import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.client.client_model import CreateClient, UpdateAllClient, UpdateClient
from mapa.manage.client.client_service import ClientService
from mapa.manage.tenant_client.tenant_client_service import TenantClientService
from .conftest import SsoFixture


async def create_service(fixture: SsoFixture) -> ClientService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    tenant_client_service = TenantClientService(async_db)
    client_service = ClientService(async_db, tenant_client_service)
    return client_service


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    service: ClientService = await create_service(fixture)

    assert service is not None


@pytest.mark.asyncio
async def test_get_client_info(fixture: SsoFixture):
    """Service"""
    service: ClientService = await create_service(fixture)
    assert service is not None

    client_info = await service.get_client_info(fixture.client_id)
    assert client_info is not None and client_info.client_id == fixture.client_id


@pytest.mark.asyncio
async def test_crud_client(fixture: SsoFixture):
    """Service"""

    service: ClientService = await create_service(fixture)
    assert service is not None

    # Boş bir sorgulama yapılır
    empty_item = await service.get(uuid.UUID("9ba9c88f-f5fc-4553-88a4-0d6507d49d84"), tenant_id=str(fixture.tenant_id))
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (service.create(CreateClient(
        name=f"Test_Client_{i}",
        client_id=f"Test_Client_Id_{i}",
        client_secret=f"Test_Client_Secret_{i}",
        grant_types=["implicit", "authorization code", "hybrid"]
    ), str(fixture.tenant_id)) for i in range(1, el_count + 1))

    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), str(fixture.tenant_id))
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_X"
    first_item = items[0]

    updated_first_item = await service.update(first_item.id, UpdateClient(
        name=test_value
    ), str(fixture.tenant_id))    
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # isme göre arama yapılır
    updated_first_item_2 = await service.get_by_name(test_value, str(fixture.tenant_id))
    assert updated_first_item_2 is not None
    assert updated_first_item_2.name == test_value

    # Client ID değerine göre arama yapılır.
    updated_first_item_2 = await service.get_by_client_id(first_item.client_id, str(fixture.tenant_id))
    assert updated_first_item_2 is not None
    assert updated_first_item_2.client_id == first_item.client_id

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="name", op=FilterOp.ILIKE, value="Test_Client_%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await service.update_all(query_args_update, UpdateAllClient(
        name=test_value_2
    ), str(fixture.tenant_id))
    assert updated_el_count == len(items) - 1

    # ikinci eleman sorgulanır
    updated_first_item = await service.get(items[2].id, str(fixture.tenant_id))
    assert updated_first_item is not None
    assert updated_first_item.name == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await service.delete(updated_first_item.id, str(fixture.tenant_id))
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await service.delete_by_ids(last_item_ids, str(fixture.tenant_id))
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="name", op=FilterOp.ILIKE, value=test_value_2)
    ])
    deleted_row_count = await service.delete_all(query_args_delete, str(fixture.tenant_id))
    assert deleted_row_count == len(items) - 1 - 3

    # Silinenler sorgulanır
    deleted_rows = await service.find(query_args_delete, str(fixture.tenant_id))
    assert len(deleted_rows) == 0
