import asyncio
import pytest
from mapa.gateway.constant import ConnectionInfoTypes
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.connection_info.connection_info_model import CreateConnectionInfo
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService
from .conftest import GatewayFixture, generate_authorization_info, generate_gateway_api, generate_integration, generate_request_parameter_mapping, generate_response_parameter_mapping, tenant_id
from uuid import uuid4
from typing import Any, Dict
from unittest.mock import Mock

from mapa.gateway.route.route_model import Route, CreateRoute, UpdateAllRoute, UpdateRoute
from mapa.gateway.route.route_service import RouteService

from mapa.gateway.gateway_api.gateway_api_model import GatewayApi, CreateGatewayApi, UpdateAllGatewayApi, UpdateGatewayApi
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService

from mapa.gateway.integration.integration_model import Integration, CreateIntegration, UpdateAllIntegration, UpdateIntegration
from mapa.gateway.integration.integration_service import IntegrationService

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
        "parameter_mapping_service": ParameterMappingService(async_db),
        "connection_info_service": connection_info_service,
    }

@pytest.mark.asyncio
async def test_create_service(fixture: GatewayFixture):
    """Service"""
    services = await create_services(fixture)
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    integration_service: IntegrationService = services["integration_service"]
    parameter_mapping_service: ParameterMappingService = services["parameter_mapping_service"]
    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    assert connection_info_service is not None
    assert gateway_api_service is not None
    assert integration_service is not None
    assert parameter_mapping_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: GatewayFixture):
    """IntegrationParameterMappingService Crud Test"""
    services = await create_services(fixture)
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    integration_service: IntegrationService = services["integration_service"]
    parameter_mapping_service: ParameterMappingService = services["parameter_mapping_service"]
    connection_info_service: ConnectionInfoService = services["connection_info_service"]
    
    assert connection_info_service is not None
    assert gateway_api_service is not None
    assert integration_service is not None
    assert parameter_mapping_service is not None
    
    # Api oluşturulur
    create_gateway_api: CreateGatewayApi = generate_gateway_api()
    gateway_api: GatewayApi = await gateway_api_service.create(create_gateway_api, tenant_id)
    assert gateway_api is not None

    # Boş bir sorgulama yapılır
    empty_item_gateway_api = await gateway_api_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item_gateway_api is None
    
    # AuthorizationIfo
    auth_info = await connection_info_service.create(CreateConnectionInfo(
        name="test_auth_info2",
        description="test_auth_info_desc2",
        params=generate_authorization_info().dict(),
        type=ConnectionInfoTypes.AUTHENTICATION
    ), tenant_id=tenant_id)
    
    assert auth_info is not None
    assert auth_info.params is not None
    
    # integration oluşturulur
    create_integration: CreateIntegration = generate_integration(gateway_api.id,auth_info.id)
    integration: Integration = await integration_service.create(create_integration, tenant_id)
    assert integration is not None
    
    selected_integration = await integration_service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.EQUAL, value=integration.id)
    ]), tenant_id=tenant_id)
    assert selected_integration[0].id == integration.id
    
    # request mapping oluşturulur 
    create_request_mapping: CreateParameterMapping = generate_request_parameter_mapping(0,integration.id)
    request_mapping: ParameterMapping = await parameter_mapping_service.create(create_request_mapping, tenant_id)
    assert request_mapping is not None
    
    # response mapping oluşturulur 
    create_response_mapping: CreateParameterMapping = generate_response_parameter_mapping(200,integration.id)
    response_mapping: ParameterMapping = await parameter_mapping_service.create(create_response_mapping, tenant_id)
    assert response_mapping is not None
    
    query_args_mapping = QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[response_mapping.id,request_mapping.id])
    ])
    
    # mapping sorgulanır  
    selected_mapping = await parameter_mapping_service.find(query_args_mapping, tenant_id=tenant_id)
    assert len(selected_mapping) == 2
    
    # mapping silinir 
    deleted_row_count_mapping = await parameter_mapping_service.delete_all(query_args_mapping, tenant_id=tenant_id)
    assert deleted_row_count_mapping == 2
    
    # integration silinir
    deleted_integration = await integration_service.delete(integration.id, tenant_id)
    assert deleted_integration is True
    
     # connection info silinir
    deleted_connection_info = await connection_info_service.delete(auth_info.id, tenant_id)
    assert deleted_connection_info is True
    
    # api siilinir
    deleted_gateway_api = await gateway_api_service.delete(gateway_api.id, tenant_id)
    assert deleted_gateway_api is True