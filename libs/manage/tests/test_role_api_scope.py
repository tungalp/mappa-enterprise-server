import asyncio
from typing import Any, Dict
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.role.role_model import CreateRole, UpdateAllRole, UpdateRole
from mapa.manage.role.role_service import RoleService
from mapa.manage.role_api_scope.role_api_scope_model import CreateRoleApiScope, UpdateAllRoleApiScope, UpdateRoleApiScope
from mapa.manage.role_api_scope.role_api_scope_service import RoleApiScopeService
from mapa.manage.user.user_model import CreateUser, UpdateAllUser, UpdateUser
from mapa.manage.user.user_service import UserService
from mapa.manage.api.api_model import Api, CreateApi, UpdateAllApi, UpdateApi
from mapa.manage.api.api_service import ApiService
from mapa.manage.api_scope.api_scope_model import ApiScope, CreateApiScope, UpdateApiScope, UpdateAllApiScope
from mapa.manage.api_scope.api_scope_service import ApiScopeService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.role_user.role_user_model import CreateRoleUser, UpdateAllRoleUser, UpdateRoleUser
from mapa.manage.role_user.role_user_service import RoleUserService

from .conftest import ManageFixture, generate_api, tenant_id, generate_api_scope
from uuid import uuid4
from .data import role_by_api_scope_field_list, api_scope_role_field_list


async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    # Test verisi oluşturulur

    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    api_service = ApiService(async_db)
    organization_client_service =  OrganizationClientService(async_db)
    organization_service =  OrganizationService(async_db,organization_client_service)
    return {
        "role_user_service": RoleUserService(async_db),
        "role_api_scope_service": RoleApiScopeService(async_db),
        "role_service": RoleService(async_db),
        "api_service": api_service,
        "api_scope_service": ApiScopeService(async_db),
        "organization_service": organization_service,
        "user_service": UserService(async_db, api_service,organization_service)
    }


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""

    services = await create_services(fixture)
    assert services["user_service"] is not None
    assert services["role_user_service"] is not None
    assert services["role_api_scope_service"] is not None
    assert services["role_service"] is not None
    assert services["api_service"] is not None
    assert services["api_scope_service"] is not None


@pytest.mark.asyncio
async def test_crud_role_api_scope(fixture: ManageFixture):

    """Api / ApiScope Service"""
    """Role / Role Api Scope Service"""

    services = await create_services(fixture)
    assert services["user_service"] is not None
    assert services["role_user_service"] is not None
    assert services["role_api_scope_service"] is not None
    assert services["role_service"] is not None
    assert services["api_service"] is not None
    assert services["api_scope_service"] is not None

    role_user_service: RoleUserService = services["role_user_service"]
    role_api_scope_service: RoleApiScopeService = services["role_api_scope_service"]
    role_service: RoleService = services["role_service"]
    user_service: UserService = services["user_service"]
    api_service: ApiService = services["api_service"]
    api_scope_service: ApiScopeService = services["api_scope_service"]

    assert role_user_service is not None
    assert role_api_scope_service is not None
    assert role_service is not None
    assert user_service is not None
    assert api_service is not None
    assert api_scope_service is not None

    # Api ekleme işlemi yapılır.
    create_api: CreateApi = generate_api()
    api: Api = await api_service.create(create_api, str(tenant_id))
    assert api is not None

    # Api Scope ekleme işlemi yapılır.
    create_api_scope: CreateApiScope = generate_api_scope(api.id)
    api_scope: ApiScope = await api_scope_service.create(create_api_scope, str(tenant_id))
    assert api_scope is not None

    # Boş bir role sorgulama yapılır
    empty_item = await role_service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(tenant_id))
    assert empty_item is None

    # Yeni 10 adet role kayıt oluşturulur.
    el_count = 10
    task_list = (role_service.create(CreateRole(
        name=f"Test_{i}", description=f"Test_desc_{i}"), tenant_id=str(tenant_id))
        for i in range(1, el_count + 1))
    role_items = await asyncio.gather(*task_list)
    assert role_items is not None
    assert len(role_items) == el_count

    # Id listesine göre role kayıtları getir.
    selected_items = await role_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in role_items])
    ], order={
        "name": "desc"
    }), tenant_id=str(tenant_id))
    assert len(selected_items) == el_count

    # Boş bir role api scope sorgulama yapılır
    empty_item = await role_api_scope_service.get("9ba9c88f-f5fc-4553-88a4-0d6507d49d84", tenant_id=str(tenant_id))
    assert empty_item is None

    # role api scope kayıtları eklenir.

    role_api_scopes = (role_api_scope_service.create(CreateRoleApiScope(
        role_id=item.id, api_scope_id=api_scope.id), tenant_id=str(tenant_id))
        for item in role_items)
    role_api_scope_items = await asyncio.gather(*role_api_scopes)
    assert role_api_scope_items is not None
    assert len(role_api_scope_items) == len(role_items)

    # Role sorgulanır.
    query_roleData = await role_service.get(role_items[0].id, tenant_id=str(tenant_id), field_list=list(role_by_api_scope_field_list))
    assert query_roleData.id == role_items[0].id

    # Id listesine göre role kayıtları getir.
    selected_items = await role_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in role_items])
    ], order={
        "name": "desc"
    }), tenant_id=str(tenant_id))
    assert len(selected_items) == el_count

    # Id listesine göre role api scope kayıtları getir.
    selected_items = await role_api_scope_service.find(QueryArgs(where=[
        Filter(field="role_id", op=FilterOp.IN, value=[
               str(item.id) for item in role_items])
    ], select=api_scope_role_field_list), tenant_id=str(tenant_id))
    assert len(selected_items) == el_count

    # role api scope kayıtları silinir.
    query_role_api_scope_args_delete = QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in role_api_scope_items])
    ])

    deleted_row_count = await role_api_scope_service.delete_all(query_role_api_scope_args_delete, tenant_id=str(tenant_id))
    assert deleted_row_count == len(role_api_scope_items)

    # role kayıtları silinir.
    query_role_args_delete = QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in role_items])
    ])

    deleted_row_count = await role_service.delete_all(query_role_args_delete, tenant_id=str(tenant_id))
    assert deleted_row_count == len(role_items)

    # Api Scope silinir.
    is_deleted = await api_scope_service.delete(api_scope.id, str(tenant_id))
    assert is_deleted == True

    # Api silinir
    is_deleted = await api_service.delete(api.id, str(tenant_id))
    assert is_deleted == True
