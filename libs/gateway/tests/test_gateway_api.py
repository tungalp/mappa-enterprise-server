import asyncio
import pytest
from nanoid import generate
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService
from .conftest import GatewayFixture, generate_gateway_api, tenant_id
from uuid import uuid4
from typing import Any, Dict
from unittest.mock import Mock


from mapa.gateway.gateway_api.gateway_api_model import GatewayApi, CreateGatewayApi, UpdateAllGatewayApi, UpdateGatewayApi
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService

from mapa.gateway.integration.integration_model import Integration, CreateIntegration, UpdateAllIntegration, UpdateIntegration
from mapa.gateway.integration.integration_service import IntegrationService

from mapa.gateway.route.route_model import Route, CreateRoute, UpdateAllRoute, UpdateRoute
from mapa.gateway.route.route_service import RouteService

from mapa.gateway.parameter_mapping.parameter_mapping_model import ParameterMapping, CreateParameterMapping, UpdateAllParameterMapping, UpdateParameterMapping
from mapa.gateway.parameter_mapping.parameter_mapping_service import ParameterMappingService


async def create_services(fixture: GatewayFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    route_service = RouteService(async_db)
    connection_info_service = ConnectionInfoService(async_db)
    
    # Mock messenger for testing
    mock_messenger = Mock()
    
    async def mock_create_api(*args, **kwargs):
        return {"id": str(uuid4())}
    
    async def mock_get_api(*args, **kwargs):
        return {
            "id": str(uuid4()),
            "name": "test_api",
            "identifier": "test_identifier",
            "allow_offline_access": True,
            "skip_consent_for_verifiable_first_party_clients": False,
            "token_lifetime": 3600,
            "token_lifetime_for_web": 3600,
            "signing_alg": "RS256",
            "is_system": False
        }
    
    async def mock_update_api(*args, **kwargs):
        return {"id": str(uuid4())}
    
    async def mock_delete_api(*args, **kwargs):
        return True
    
    async def mock_delete_all_apis(*args, **kwargs):
        return True
    
    mock_messenger.create_api = mock_create_api
    mock_messenger.get_api = mock_get_api
    mock_messenger.update_api = mock_update_api
    mock_messenger.delete_api = mock_delete_api
    mock_messenger.delete_all_apis = mock_delete_all_apis
    
    return {
        "gateway_api_service": GatewayApiService(async_db, mock_messenger),
        "integration_service": IntegrationService(async_db,route_service,connection_info_service),
        "route_service": route_service,
        "parameter_mapping_service": ParameterMappingService(async_db),
        "connection_info_service": connection_info_service,
    }


@pytest.mark.asyncio
async def test_create_service(fixture: GatewayFixture):
    """Service"""
    services = await create_services(fixture)
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    integration_service: IntegrationService = services["integration_service"]
    route_service: RouteService = services["route_service"]
    parameter_mapping_service: ParameterMappingService = services[
        "parameter_mapping_service"]
    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    assert connection_info_service is not None
    assert gateway_api_service is not None
    assert integration_service is not None
    assert route_service is not None
    assert parameter_mapping_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: GatewayFixture):
    """GatewayApiService Crud Test"""
    services = await create_services(fixture)
    gateway_api_service: GatewayApiService = services["gateway_api_service"]

    assert gateway_api_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await gateway_api_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None

    # Yeni 10 adet kayıt oluşturulur.
    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (gateway_api_service.create(generate_gateway_api(), tenant_id=tenant_id)
                 for i in range(1, el_count + 1))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Id listesine göre kayıtları getir
    selected_items = await gateway_api_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(item.id) for item in items])
    ], order={
        "name": "desc"
    }), tenant_id=tenant_id)
    assert len(selected_items) == el_count

    # ilk elemanın bir özniteliği değiştirilir
    test_value = "Test_XXX"
    first_item: GatewayApi = items[0]

    updated_first_item = await gateway_api_service.update(first_item.id, UpdateGatewayApi(
        name=test_value, description=test_value, path=first_item.path, identifier=first_item.identifier
    ), tenant_id=tenant_id)
    assert updated_first_item is not None
    assert updated_first_item.name == test_value

    # Bir özniteliği toplu olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="description", op=FilterOp.LIKE, value="Test%")
    ])
    test_value_2 = "mobidik"
    updated_el_count = await gateway_api_service.update_all(query_args_update, UpdateAllGatewayApi(
        description=test_value_2
    ), tenant_id=tenant_id)
    assert updated_el_count == len(items)

    # ilk elemanı sorgulanır
    updated_first_item = await gateway_api_service.get(first_item.id, tenant_id=tenant_id)
    assert updated_first_item.description == test_value_2

    # ilk kayıt silinir
    first_row_deleted = await gateway_api_service.delete(updated_first_item.id, tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_item_ids = [cust.id for cust in items[-2:]]
    deleted_row_count = await gateway_api_service.delete_by_ids(last_item_ids, tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="description", op=FilterOp.EQUAL, value=test_value_2)
    ])
    deleted_row_count = await gateway_api_service.delete_all(query_args_delete, tenant_id=tenant_id)
    assert deleted_row_count == len(items) - 3

    # Silinenler sorgulanır
    deleted_rows = await gateway_api_service.find(query_args_delete, tenant_id=tenant_id)
    assert len(deleted_rows) == 0
