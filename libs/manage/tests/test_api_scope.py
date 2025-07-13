import asyncio
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.api.api_model import Api, CreateApi, UpdateAllApi, UpdateApi
from mapa.manage.api.api_service import ApiService
from mapa.manage.api_scope.api_scope_model import ApiScope, CreateApiScope, UpdateApiScope, UpdateAllApiScope
from mapa.manage.client.client_model import Client, CreateClient, UpdateAllClient, UpdateClient
from mapa.manage.client.client_service import ClientService
from mapa.manage.client_api.client_api_model import ClientApi, CreateClientApi
from mapa.manage.client_api.client_api_service import ClientApiService
from mapa.manage.tenant_client.tenant_client_service import TenantClientService
from .conftest import ManageFixture, generate_api, generate_client_api, tenant_id, generate_api_scope, generate_client, generate_client_api_scope
from uuid import uuid4
from mapa.manage.api_scope.api_scope_service import ApiScopeService
from mapa.manage.client_api_scope.client_api_scope_service import ClientApiScopeService
from mapa.manage.client_api_scope.client_api_scope_model import CreateClientApiScope, ClientApiScope
from .data import client_api_field_list
from typing import Any, Dict


async def create_services(fixture: ManageFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    tenant_client_service = TenantClientService(async_db)
    
    api_scope_service = ApiScopeService(async_db)
    return {
        "ApiService": ApiService(async_db),
        "ClientService": ClientService(async_db, tenant_client_service,api_scope_service),
        "TenantClientService": TenantClientService(async_db),
        "ClientApiService": ClientApiService(async_db),
        "ApiService": ApiService(async_db),
        "ApiScopeService": ApiScopeService(async_db),
        "ClientApiScopeService": ClientApiScopeService(async_db),
    }


async def create_api_scope_service(fixture: ManageFixture) -> ApiScopeService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)
    return ApiScopeService(async_db)


@pytest.mark.asyncio
async def test_create_services(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    api_service: ApiService = services["ApiService"]

    assert api_service is not None

    api_scope_service: ApiScopeService = services["ApiScopeService"]
    assert api_scope_service is not None


@pytest.mark.asyncio
async def test_create_data(fixture: ManageFixture):
    """ApiScopeService Create Test"""
    services = await create_services(fixture)
    service: ApiService = services["ApiService"]
    
    assert service is not None

    create_api: CreateApi = generate_api()
    api: Api = await service.create(create_api, tenant_id)
    assert api is not None

    api_scope_service: ApiScopeService = await create_api_scope_service(fixture)
    assert api_scope_service is not None

    create_api_scope: CreateApiScope = generate_api_scope(api.id)
    api_scope: ApiScope = await api_scope_service.create(create_api_scope, tenant_id)
    assert api_scope is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: ManageFixture):
    """ApiScopeService Crud Test"""
    services = await create_services(fixture)
    service: ApiService = services["ApiService"]
    
    assert service is not None

    # Boş bir sorgulama yapılır
    empty_item = await service.get(uuid4(), tenant_id=fixture.tenant_id)
    assert empty_item is None

    createApi: CreateApi = generate_api()
    api: Api = await service.create(createApi, fixture.tenant_id)
    assert api is not None

    api_scope_service: ApiScopeService = await create_api_scope_service(fixture)
    assert api_scope_service is not None

    create_api_scope: CreateApiScope = generate_api_scope(api.id)
    api_scope: ApiScope = await api_scope_service.create(create_api_scope, tenant_id)
    assert api_scope is not None

    api = await service.get(api.id, tenant_id)
    assert api is not None

    # TODO: queryargs içinde fieldlist verildiğinde çalışmıyor, excp atıyor
    # queryArgs = QueryArgs(where=[
    #    Filter(field="id", op=FilterOp.Equal, value=[api.id])
    # ], select=field_list)

    # Id listesine göre kayıtları getir
    # selected_items = await service.find(queryArgs, tenant_id=fixture.tenant_id)

    isDeleted = await api_scope_service.delete(api_scope.id, tenant_id)
    assert isDeleted == True

    isDeleted = await service.delete(api.id, tenant_id)
    assert isDeleted == True
