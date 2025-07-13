import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict
from uuid import uuid4
import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.user.user_model import CreateUser
from mapa.manage.user.user_service import UserService
from mapa.sso.user_session.user_session_model import CreateUserSession, UpdateAllUserSession, UpdateUserSession
from mapa.sso.user_session.user_session_service import UserSessionService
from mapa.sso.user_session_client.user_session_client_service import UserSessionClientService
from .conftest import SsoFixture
from ..data import user as default_user
from mapa.manage.api.api_service import ApiService


async def create_services(fixture: SsoFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)  
    organization_client_service = OrganizationClientService(async_db)   
    organization_service = OrganizationService(async_db,organization_client_service)
   
    return {
        "user_session": UserSessionService(async_db),
        "user": UserService(async_db,api_service,organization_service),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    services = await create_services(fixture)

    assert services["user_session"] is not None
    assert services["user"] is not None

@pytest.mark.asyncio
async def test_crud_user_session(fixture: SsoFixture):
    """Service"""
    services = await create_services(fixture)
    
    assert services["user_session"] is not None
    assert services["user"] is not None
    
    service: UserSessionService = services["user_session"]
    user_service: UserService = services["user"]

    
    # Boş bir sorgulama yapılır
    empty_item = await service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84")
    assert empty_item is None
    
    user = await user_service.create(CreateUser(name="test", surname="test", email="test@test.com.com",password="123", phone="123"))
    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (service.create(CreateUserSession(
        id=uuid4(),
        user_id=user.id,  # type: ignore
        authenticated_at=datetime.now(),
        authenticated=True,
        expired_at=datetime.now() + timedelta(minutes=10080)))
        for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[str(item.id) for item in items])
    ], order={
        "authenticated_at": "desc"
    }))
    assert len(selected_items) == el_count
    
    # ilk elemanın bir özniteliği değiştirilir
    test_value = datetime(2023, 1, 1)
    first_item = items[0]

    updated_first_item = await service.update(first_item.id, UpdateUserSession(
        expired_at=test_value,
        authenticated=False
    ))
    assert updated_first_item is not None
    assert updated_first_item.expired_at == test_value
    assert updated_first_item.authenticated == False

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="user_id", op=FilterOp.EQUAL, value=user.id)
    ])
    test_value_2 = datetime(2023, 1, 2)
    updated_el_count = await service.update_all(query_args_update, UpdateAllUserSession(
        expired_at=test_value_2,
        authenticated=True
    ))
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await service.get(first_item.id)
    assert updated_first_item.expired_at == test_value_2
    
    # ilk kayıt silinir
    first_row_deleted = await service.delete(updated_first_item.id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await service.delete_by_ids(last_item_ids)
    assert deleted_row_count == 2
        
    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="user_id", op=FilterOp.EQUAL, value=user.id)
    ])
    deleted_row_count = await service.delete_all(query_args_delete)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await service.find(query_args_delete)
    assert len(deleted_rows) == 0

