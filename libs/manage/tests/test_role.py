import asyncio
from typing import Any, Dict
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.role.role_model import CreateRole, UpdateAllRole, UpdateRole
from mapa.manage.role_user.role_user_model import CreateRoleUser, UpdateAllRoleUser, UpdateRoleUser
from mapa.manage.role_user.role_user_service import RoleUserService
from mapa.manage.role.role_service import RoleService
from .conftest import ManageFixture
from mapa.manage.user.user_model import CreateUser, UpdateAllUser, UpdateUser
from mapa.manage.user.user_service import UserService
from mapa.manage.api.api_model import Api, CreateApi, UpdateAllApi, UpdateApi
from mapa.manage.api.api_service import ApiService
from mapa.manage.api_scope.api_scope_model import ApiScope, CreateApiScope, UpdateApiScope, UpdateAllApiScope
from mapa.manage.api_scope.api_scope_service import ApiScopeService
from mapa.manage.role_api_scope.role_api_scope_model import CreateRoleApiScope, UpdateAllRoleApiScope, UpdateRoleApiScope
from mapa.manage.role_api_scope.role_api_scope_service import RoleApiScopeService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService


async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)
    organization_client_service = OrganizationClientService(async_db)
    organization_service = OrganizationService(async_db,organization_client_service)
    return {
        "role_user_service": RoleUserService(async_db),
        "role_service": RoleService(async_db),  
        "organization_service": organization_service,
        "user_service": UserService(async_db, api_service, organization_service),
        "api_service": api_service,
        "api_scope_service": ApiScopeService(async_db),
        "role_api_scope_service": RoleApiScopeService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    assert services["role_user_service"] is not None
    assert services["role_service"] is not None
    assert services["user_service"] is not None
    assert services["api_service"] is not None
    assert services["api_scope_service"] is not None
    assert services["role_api_scope_service"] is not None


@pytest.mark.asyncio
async def test_crud_role(fixture: ManageFixture):
    """Service"""

    services = await create_services(fixture)
    assert services["role_user_service"] is not None
    assert services["role_service"] is not None
    assert services["user_service"] is not None
    assert services["api_service"] is not None
    assert services["api_scope_service"] is not None
    assert services["role_api_scope_service"] is not None

    role_user_service: RoleUserService = services["role_user_service"]
    role_service: RoleService = services["role_service"]
    user_service: UserService = services["user_service"]
    api_service: ApiService = services["api_service"]
    api_scope_service: ApiScopeService = services["api_scope_service"]
    role_api_scope_service: RoleApiScopeService = services["role_api_scope_service"]

    assert role_user_service is not None
    assert role_service is not None
    assert user_service is not None
    assert api_service is not None
    assert api_scope_service is not None
    assert role_api_scope_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await role_service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(fixture.tenant_id))
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (role_service.create(CreateRole(
        name=f"Test_{i}", description=f"Test_desc_{i}"), tenant_id=str(fixture.tenant_id))
        for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await role_service.find(QueryArgs(where=[
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
    selected_one = await role_service.get_by_role_id(first_item.id, tenant_id=str(fixture.tenant_id))
    assert selected_one.id == first_item.id

    updated_first_item = await role_service.update(first_item.id, UpdateRole(
        name=test_value, description=test_value
    ), tenant_id=str(fixture.tenant_id))
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="description", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await role_service.update_all(query_args_update, UpdateAllRole(
        description=test_value_2
    ), tenant_id=str(fixture.tenant_id))
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await role_service.get(first_item.id, tenant_id=str(fixture.tenant_id))
    assert updated_first_item.description == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await role_service.delete(updated_first_item.id, str(fixture.tenant_id))
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await role_service.delete_by_ids(last_item_ids, str(fixture.tenant_id))
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="description", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await role_service.delete_all(query_args_delete, tenant_id=str(fixture.tenant_id))
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await role_service.find(query_args_delete, tenant_id=str(fixture.tenant_id))
    assert len(deleted_rows) == 0
