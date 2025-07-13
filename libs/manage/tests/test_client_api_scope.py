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
        "ClientApiService": ClientApiService(async_db),
        "TenantClientService": TenantClientService(async_db),
        "ApiService": ApiService(async_db),
        "ApiScopeService": ApiScopeService(async_db),
        "ClientApiScopeService": ClientApiScopeService(async_db),
    }

@pytest.mark.asyncio
async def test_create_services(fixture: ManageFixture):
    services = await create_services(fixture)
    
    api_service: ApiService = services["ApiService"]
    api_scope_service: ApiScopeService = services["ApiScopeService"]
    client_service: ClientService = services["ClientService"]
    client_api_service: ClientApiService = services["ClientApiService"]
    client_api_scope_service: ClientApiScopeService =  services["ClientApiScopeService"]

    assert api_service is not None
    assert api_scope_service is not None
    assert client_service is not None
    assert client_api_service is not None
    assert client_api_scope_service is not None

@pytest.mark.asyncio
async def test_create_data(fixture: ManageFixture):
    """ApiScopeService Create Test"""
    services = await create_services(fixture)
    
    api_service: ApiService = services["ApiService"]
    api_scope_service: ApiScopeService = services["ApiScopeService"]
    client_service: ClientService = services["ClientService"]
    client_api_service: ClientApiService = services["ClientApiService"]
    client_api_scope_service: ClientApiScopeService =  services["ClientApiScopeService"]

    assert api_service is not None
    assert api_scope_service is not None
    assert client_service is not None
    assert client_api_service is not None
    assert client_api_scope_service is not None

    create_api: CreateApi = generate_api()
    api: Api = await api_service.create(create_api, str(tenant_id))
    assert api is not None

    create_api_scope: CreateApiScope = generate_api_scope(api.id)
    api_scope: ApiScope = await api_scope_service.create(create_api_scope, str(tenant_id))
    assert api_scope is not None

    create_client = CreateClient = generate_client()
    client: Client = await client_service.create(create_client, str(tenant_id))
    assert client is not None

    create_client_api: CreateClientApi = generate_client_api(
        client.id, api.id)
    client_api: ClientApi = await client_api_service.create(create_client_api, str(tenant_id))
    assert client_api is not None

    create_client_api_scope: CreateClientApiScope = generate_client_api_scope(
        client_api.id, api_scope.id)
    client_api_scope: ClientApiScope = await client_api_scope_service.create(create_client_api_scope, str(tenant_id))
    assert client_api_scope is not None

    client_api_s = await client_api_service.get(client_api.id, str(tenant_id), client_api_field_list)
    assert client_api_s is not None

