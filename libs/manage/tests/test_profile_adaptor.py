import asyncio
import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.profile_adaptor.profile_adaptor_model import CreateProfileAdaptor, UpdateAllProfileAdaptor, UpdateProfileAdaptor
from mapa.manage.profile_adaptor.profile_adaptor_service import ProfileAdaptorService
from .conftest import ManageFixture


async def create_service(fixture: ManageFixture) -> ProfileAdaptorService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    return ProfileAdaptorService(async_db)


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    service: ProfileAdaptorService = await create_service(fixture)

    assert service is not None

@pytest.mark.asyncio
async def test_crud_profile_adaptor(fixture: ManageFixture):
    """Service"""
    service: ProfileAdaptorService = await create_service(fixture)
    assert service is not None
    
    # Boş bir sorgulama yapılır
    empty_item = await service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=fixture.tenant_id)
    assert empty_item is None
    
    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (service.create(CreateProfileAdaptor(
        user_info_endpoint="Test",user_info_list_endpoint="Test"), tenant_id=fixture.tenant_id)
        for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[str(item.id) for item in items])
    ], order={
        "user_info_endpoint": "desc"
    }), tenant_id=fixture.tenant_id)
    assert len(selected_items) == el_count
    
    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_X"
    first_item = items[0]

    # birinci elamanın bilgisini döner
    selected_one = await service.get_by_profile_adaptor_id(first_item.id,tenant_id=fixture.tenant_id)
    assert selected_one.id == first_item.id

    updated_first_item = await service.update(first_item.id, UpdateProfileAdaptor(
        user_info_endpoint=test_value
    ), tenant_id=fixture.tenant_id)
    assert updated_first_item.user_info_endpoint == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="user_info_list_endpoint", op=FilterOp.EQUAL, value="Test")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await service.update_all(query_args_update, UpdateAllProfileAdaptor(
        user_info_endpoint=test_value_2,user_info_list_endpoint=test_value_2
    ), tenant_id=fixture.tenant_id)
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await service.get(first_item.id)
    assert updated_first_item.user_info_endpoint == test_value_2
    
    # ilk kayıt silinir
    first_row_deleted = await service.delete(updated_first_item.id, fixture.tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await service.delete_by_ids(last_item_ids, fixture.tenant_id)
    assert deleted_row_count == 2
        
    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="user_info_endpoint", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await service.delete_all(query_args_delete, tenant_id=fixture.tenant_id)
    assert deleted_row_count == len(items) - 3 

    # Silinenler sorgulanır
    deleted_rows = await service.find(query_args_delete, tenant_id=fixture.tenant_id)
    assert len(deleted_rows) == 0
