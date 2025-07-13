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
        "TenantClientService": tenant_client_service,
        "ApiService": ApiService(async_db),
        "ApiScopeService": ApiScopeService(async_db),
        "ClientApiScopeService": ClientApiScopeService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: ManageFixture):
    """Service"""
    services = await create_services(fixture)
    service: ClientService = services["ClientService"]

    assert service is not None


@pytest.mark.asyncio
async def test_create_data(fixture: ManageFixture):
    """ClientService Create Test"""
    services = await create_services(fixture)
    service: ClientService = services["ClientService"]

    assert service is not None

    createClient: CreateClient = generate_client()
    client: Client = await service.create(createClient, str(tenant_id))
    assert client is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: ManageFixture):
    """ClientService Crud Test"""
    services = await create_services(fixture)
    service: ClientService = services["ClientService"]

    assert service is not None

    # Boş bir sorgulama yapılır
    empty_item = await service.get(uuid4(), tenant_id=str(tenant_id))
    assert empty_item is None

    createClient: CreateClient = generate_client()
    client = await service.create(createClient, str(tenant_id))
    assert client is not None

    client = await service.get(client.id, str(tenant_id))
    assert client is not None

    client = await service.get_by_client_id(str(client.client_id), tenant_id=str(tenant_id))
    assert client is not None

    isDeleted = await service.delete(client.id)
    assert isDeleted == True


@pytest.mark.asyncio
async def test_query(fixture: ManageFixture):
    """ClientService Crud Test"""
    services = await create_services(fixture)
    service: ClientService = services["ClientService"]

    assert service is not None

    # Boş bir sorgulama yapılır
    empty_item = await service.get(uuid4(), tenant_id=str(tenant_id))
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (service.create(generate_client(), str(tenant_id))
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    queryArgs = QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], limit=0, offset=0)

    # Id listesine göre kayıtları getir
    selected_items = await service.find(queryArgs, tenant_id=str(tenant_id))
    assert len(selected_items) == el_count

    # Id listesine göre kayıtları siler
    deleted_count = await service.delete_all(queryArgs, tenant_id=str(tenant_id))
    assert len(selected_items) == deleted_count
