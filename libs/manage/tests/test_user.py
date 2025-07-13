import asyncio
import pytest
from datetime import datetime, timedelta
from random import random
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.invitation.invitation_model import CreateInvitation
from mapa.manage.invitation.invitation_util_service import InvitationUtilService
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.tenant_user.tenant_user_model import CreateTenantUser
from mapa.manage.tenant_user.tenant_user_service import TenantUserService
from mapa.manage.user.user_model import CreateUser, UpdateAllUser, UpdateUser
from mapa.manage.user.user_service import UserService
from .conftest import ManageFixture
from typing import Any, Dict
from mapa.manage.api.api_model import Api, CreateApi, UpdateAllApi, UpdateApi
from mapa.manage.api.api_service import ApiService
from mapa.manage.api_scope.api_scope_model import ApiScope, CreateApiScope, UpdateApiScope, UpdateAllApiScope
from mapa.manage.api_scope.api_scope_service import ApiScopeService
from mapa.manage.role.role_model import CreateRole, UpdateAllRole, UpdateRole
from mapa.manage.role.role_service import RoleService
from mapa.manage.profile_adaptor.profile_adaptor_model import CreateProfileAdaptor, UpdateAllProfileAdaptor, UpdateProfileAdaptor
from mapa.manage.profile_adaptor.profile_adaptor_service import ProfileAdaptorService
from mapa.manage.role_user.role_user_model import CreateRoleUser, UpdateAllRoleUser, UpdateRoleUser
from mapa.manage.role_user.role_user_service import RoleUserService
from mapa.manage.invitation.invitation_service import InvitationService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService


async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)

    fixture_manage = ManageFixture()
    initialized_manage = await fixture_manage.create_test_data()
    assert initialized_manage is True
    async_db_manage = fixture_manage.create_db_instance(fixture_manage.db_url_async)
    api_service = ApiService(async_db_manage)
    organization_client_service = OrganizationClientService(async_db)
    organization_service = OrganizationService(async_db, organization_client_service)
  
    return {
        "api_service": api_service,
        "api_scope_service": ApiScopeService(async_db_manage),
        "role_service": RoleService(async_db_manage),
        "role_user_service": RoleUserService(async_db_manage),
        "profile_adaptor_service": ProfileAdaptorService(async_db_manage),   
        "organization_service": organization_service,
        "user_service": UserService(async_db, api_service, organization_service),
        "invitation_service": InvitationService(async_db),
        "tenant_user_service": TenantUserService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)

    assert services["profile_adaptor_service"] is not None
    assert services["user_service"] is not None
    assert services["role_user_service"] is not None
    assert services["role_service"] is not None
    assert services["api_service"] is not None
    assert services["api_scope_service"] is not None
    assert services["invitation_service"] is not None
    assert services["tenant_user_service"] is not None


@pytest.mark.asyncio
async def test_user_scopes(fixture: ManageFixture):
    services = await create_services(fixture)
    assert services["profile_adaptor_service"] is not None
    assert services["user_service"] is not None
    assert services["role_user_service"] is not None
    assert services["role_service"] is not None
    assert services["api_service"] is not None
    assert services["api_scope_service"] is not None
    assert services["invitation_service"] is not None
    assert services["tenant_user_service"] is not None

    user_service: UserService = services["user_service"]
    # birinci elamanın bilgisini döner
    user_scopes = await user_service.get_user_scopes("fa2518dd-5b27-4a59-b740-e96c3c79160a", "7175e67d-0ddc-4c96-a167-c3f3ef72de5a", tenant_id=str(fixture.tenant_id))
    assert 1 == 1


@pytest.mark.asyncio
async def test_crud_user(fixture: ManageFixture):
    """Service"""

    services = await create_services(fixture)
    assert services["profile_adaptor_service"] is not None
    assert services["user_service"] is not None
    assert services["role_user_service"] is not None
    assert services["role_service"] is not None
    assert services["api_service"] is not None
    assert services["api_scope_service"] is not None
    assert services["invitation_service"] is not None
    assert services["tenant_user_service"] is not None

    profile_adaptor_service: ProfileAdaptorService = services["profile_adaptor_service"]
    user_service: UserService = services["user_service"]
    role_user_service: RoleUserService = services["role_user_service"]
    role_service: RoleService = services["role_service"]
    api_service: ApiService = services["api_service"]
    api_scope_service: ApiScopeService = services["api_scope_service"]
    tenant_user_service: TenantUserService = services["tenant_user_service"]

    assert profile_adaptor_service is not None
    assert user_service is not None
    assert role_user_service is not None
    assert role_service is not None
    assert api_service is not None
    assert api_scope_service is not None
    assert tenant_user_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await user_service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(fixture.tenant_id))
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (user_service.create(CreateUser(
        name=f"Test_{i}", surname="Test",
        email=f"test_{i}@gmail.com", password=f"p@ssw0rd{i}",
        subject_id=f"{i}", phone=f"{i}"),
        tenant_id=str(fixture.tenant_id))
        for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_user_items = await user_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), tenant_id=str(fixture.tenant_id))
    assert len(selected_user_items) == el_count

    # Tenant User eklenir
    tenant_user_task_list = (tenant_user_service.create(CreateTenantUser(
      user_id=selected_user_items[i].id,role= "member",tenant_id=fixture.tenant_id),
        tenant_id=str(fixture.tenant_id))
        for i in range(0, len(selected_user_items)))
    tenant_user_items = await asyncio.gather(*tenant_user_task_list)
    assert tenant_user_items is not None
    assert len(tenant_user_items) == len(selected_user_items)


    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_X"
    first_item = items[0]

    # birinci elamanın bilgisini döner
    selected_one = await user_service.get_by_user_id(first_item.id, tenant_id=str(fixture.tenant_id))
    assert selected_one.id == first_item.id

    updated_first_item = await user_service.update(first_item.id, UpdateUser(
        name=test_value
    ), tenant_id=str(fixture.tenant_id))
    assert updated_first_item is not None 
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="surname", op=FilterOp.EQUAL, value="Test")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await user_service.update_all(query_args_update, UpdateAllUser(
        surname=test_value_2
    ), tenant_id=str(fixture.tenant_id))
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await user_service.get(first_item.id, tenant_id=str(fixture.tenant_id))
    assert updated_first_item.surname == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await user_service.delete(updated_first_item.id, str(fixture.tenant_id))
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await user_service.delete_by_ids(last_item_ids, str(fixture.tenant_id))
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="surname", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await user_service.delete_all(query_args_delete, tenant_id=str(fixture.tenant_id))
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await user_service.find(query_args_delete, tenant_id=str(fixture.tenant_id))
    assert len(deleted_rows) == 0
