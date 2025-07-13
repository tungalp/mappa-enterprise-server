import asyncio
import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.role_user.role_user_model import CreateRoleUser, UpdateAllRoleUser, UpdateRoleUser
from mapa.manage.role_user.role_user_service import RoleUserService
from .conftest import ManageFixture, tenant_id
from datetime import datetime, timedelta
from typing import Any, Dict
from .data import role_by_user_field_list, user_by_role_field_list, role_user_field_list
from mapa.manage.user.user_model import CreateUser, UpdateAllUser, UpdateUser
from mapa.manage.user.user_service import UserService
from mapa.manage.role.role_model import CreateRole, UpdateAllRole, UpdateRole
from mapa.manage.role.role_service import RoleService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.api.api_model import Api, CreateApi, UpdateAllApi, UpdateApi
from mapa.manage.api.api_service import ApiService
from mapa.manage.api_scope.api_scope_model import ApiScope, CreateApiScope, UpdateApiScope, UpdateAllApiScope
from mapa.manage.api_scope.api_scope_service import ApiScopeService
from mapa.manage.role_api_scope.role_api_scope_model import CreateRoleApiScope, UpdateAllRoleApiScope, UpdateRoleApiScope
from mapa.manage.role_api_scope.role_api_scope_service import RoleApiScopeService


async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)
    organization_client_service= OrganizationClientService(async_db)
    organization_service= OrganizationService(async_db,organization_client_service)
    return {
        "role_user_service": RoleUserService(async_db),
        "role_service": RoleService(async_db),
        "api_service": api_service,
        "organization_service": organization_service,
        "user_service": UserService(async_db, api_service,organization_service),
        "api_scope_service": ApiScopeService(async_db),
        "role_api_scope_service": RoleApiScopeService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service_manage(fixture: ManageFixture):
    """MANAGE Service"""
    services = await create_services(fixture)

    assert services["role_user_service"] is not None
    assert services["role_service"] is not None
    assert services["user_service"] is not None
    assert services["api_service"] is not None
    assert services["api_scope_service"] is not None
    assert services["role_api_scope_service"] is not None


@pytest.mark.asyncio
async def test_crud_role_user(fixture: ManageFixture):
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
    empty_item = await role_user_service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(tenant_id))
    assert empty_item is None

    # Role eklenir.
    roleData = await role_service.create(CreateRole(
        name="Test_role_name", description="Test_role_desc"), str(tenant_id))
    assert roleData is not None

    # User eklenir.
    userData = await user_service.create(CreateUser(
        name=f"Test_user", surname="Test_user",
        email=f"test_@gmail.com", password="1123124",
        subject_id="1123123", phone="1"), str(tenant_id))
    assert userData is not None

    userData2 = await user_service.create(CreateUser(
        name=f"name_2222222", surname="Test_user_222",
        email=f"test_2222@gmail.com", password="2222222",
        subject_id="222222", phone="2222222"), str(tenant_id))
    assert userData2 is not None

    user_list = [userData, userData2]

    # Role-User ilişkisi eklenir
    date = datetime(2023, 1, 1)

    roleUserData = await role_user_service.create(CreateRoleUser(
        role_id=roleData.id, user_id=userData.id, expired_at=date), str(tenant_id))

    assert roleUserData is not None

    roleUserData2 = await role_user_service.create(CreateRoleUser(
        role_id=roleData.id, user_id=userData2.id, expired_at=date), str(tenant_id))

    assert roleUserData2 is not None

    # birinci elamanın bilgisini döner
    selected_one = await role_user_service.get_by_role_user_id(roleUserData.id, tenant_id=str(tenant_id))
    assert selected_one.id == roleUserData.id

    # Eklenen role-user ilişkisi sorgulanır
    query_roleUserData = await role_user_service.get(roleUserData.id, field_list=list(role_user_field_list))
    assert query_roleUserData is not None

    # Role sorgulanır.
    query_roleData = await role_service.get(roleData.id, tenant_id=str(tenant_id), field_list=list(role_by_user_field_list))
    assert query_roleData.id == roleData.id

    # User sorgulanır.
    query_userData = await user_service.get(userData.id, tenant_id=str(tenant_id), field_list=list(user_by_role_field_list))
    assert query_userData.id == userData.id

    # Eklenen role-user ilişkisi silinir
    deleted_roleUserData = await role_user_service.delete(roleUserData.id)
    assert deleted_roleUserData == True

    query_args_delete_all = QueryArgs(where=[
        Filter(field="role_id", op=FilterOp.EQUAL, value=roleData.id)
    ])

    deleted_roleUserData_all = await role_user_service.delete_all(query_args_delete_all, tenant_id=str(tenant_id))
    assert deleted_roleUserData_all == True

    # Role sorgulanır.
    query_roleData1 = await role_service.get(roleData.id, tenant_id=str(tenant_id))
    assert query_roleData1.id == roleData.id

    # Role silinir.
    deleted_roleData = await role_service.delete(roleData.id)
    assert deleted_roleData is not None

    # User silinir.
    user_list_ids = [lst.id for lst in user_list]
    deleted_userData = await user_service.delete_by_ids(user_list_ids, tenant_id=str(tenant_id))
    assert deleted_userData is not None
