import pytest
from mapa.gateway.connection_info.authentication_info_model import AuthenticationInfo
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo, CreateConnectionInfo
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService
from mapa.gateway.connection_info.database_info_model import DatabaseInfo
from mapa.gateway.constant import AuthenticationInfoTypes, ConnectionInfoTypes, IntegrationTypes
from mapa.gateway.route.route_service import RouteService
from .conftest import GatewayFixture, generate_authorization_info, generate_database_info, generate_database_info_esp_test,generate_database_info_islem_oracle,tenant_id


from mapa.gateway.gateway_api.gateway_api_model import GatewayApi, CreateGatewayApi, UpdateAllGatewayApi, UpdateGatewayApi
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService

from mapa.gateway.integration.integration_model import Integration, CreateIntegration, UpdateAllIntegration, UpdateIntegration
from mapa.gateway.integration.integration_service import IntegrationService

from mapa.gateway.parameter_mapping.parameter_mapping_model import ParameterMapping, CreateParameterMapping, UpdateAllParameterMapping, UpdateParameterMapping
from mapa.gateway.parameter_mapping.parameter_mapping_service import ParameterMappingService

from uuid import uuid4
from typing import Any, Dict, List
from unittest.mock import Mock

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
        "connection_info_service": connection_info_service,
        "integration_service": IntegrationService(async_db,route_service,connection_info_service),
        "route_service": route_service,
        "parameter_mapping_service": ParameterMappingService(async_db),
    }

    

@pytest.mark.asyncio
async def test_create_service(fixture: GatewayFixture):
    """Service"""
    services = await create_services(fixture)
    connection_info_service: ConnectionInfoService = services["connection_info_service"]
    integration_service: IntegrationService = services["integration_service"]
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    route_service: RouteService = services["route_service"]
    parameter_mapping_service: ParameterMappingService = services["parameter_mapping_service"]
    
    assert parameter_mapping_service is not None
    assert route_service is not None
    assert connection_info_service is not None
    assert integration_service is not None
    assert gateway_api_service is not None


@pytest.mark.asyncio
async def test_create_data_and_query_and_delete(fixture: GatewayFixture):
    """ConnectionInfoService Crud Test"""
    
    services = await create_services(fixture)
    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    assert connection_info_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await connection_info_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None
    
    # AuthorizationIfo
    auth_info = await connection_info_service.create(CreateConnectionInfo(
        name="test_auth_info",
        description="test_auth_info_desc",
        params=generate_authorization_info().model_dump(),
        type=ConnectionInfoTypes.AUTHENTICATION
    ), tenant_id=tenant_id)
    
    assert auth_info is not None
    assert auth_info.params is not None
    
    db_info_params = AuthenticationInfo(**auth_info.params)
    assert db_info_params is not None


    # DatabaseIfo
    db_info = await connection_info_service.create(CreateConnectionInfo(
        name="test_db_info",
        description="test_db_info_desc",
        params=generate_database_info().model_dump(),
        type=ConnectionInfoTypes.DATABASE
    ), tenant_id=tenant_id)
    
    assert db_info is not None
    assert db_info.params is not None
    
    db_info_params = DatabaseInfo(**db_info.params)
    assert db_info_params is not None


         
     
@pytest.mark.asyncio
async def test_db_connection_success_list(fixture: GatewayFixture):
    """Db Connection Test"""
    
    services = await create_services(fixture)
    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    assert connection_info_service is not None

    # Boş bir sorgulama yapılır
    empty_item = await connection_info_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None
    
    # DatabaseIfo
    db_info = await connection_info_service.create(CreateConnectionInfo(
        name="test_db_info_esp_test",
        description="test_db_desc_esp_test",
        params=generate_database_info_esp_test().model_dump(),
        type=ConnectionInfoTypes.DATABASE
    ), tenant_id=tenant_id)
    
    assert db_info is not None
    assert db_info.params is not None
    
    db_info_params = DatabaseInfo(**db_info.params)
    assert db_info_params is not None
    
    result = await  connection_info_service.isConnectList([str(db_info.id)] , tenant_id=tenant_id)
    assert len(result) is not None
    
    
@pytest.mark.asyncio
async def test_db_connection_success(fixture: GatewayFixture):
    """Db Connection Test"""
    
    services = await create_services(fixture)
    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    assert connection_info_service is not None
    
    database_info= DatabaseInfo(
                     dialect ="postgresql",
                     username = "mapa", 
                     password = "12345Abc.",
                     host = "localhost",
                     port = 5432,
                     database = "mapa_test")
    
    connection_info : CreateConnectionInfo = CreateConnectionInfo(
        name="test_db_info_mapa_test",
        description="test_db_desc_mapa_test",
        type=ConnectionInfoTypes.DATABASE,
        params=database_info.model_dump())

    result : CreateConnectionInfo= await  connection_info_service.isConnect( connection_info , tenant_id=tenant_id)
    assert result is not None
    assert result.params is not None
    assert result.params["is_success"] is True
    
@pytest.mark.asyncio
async def test_db_connection_success_oracle(fixture: GatewayFixture):
    """Db Connection Test"""
    
    services = await create_services(fixture)
    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    assert connection_info_service is not None
    
    database_info = generate_database_info_islem_oracle()
    
    connection_info : CreateConnectionInfo = CreateConnectionInfo(
        name="test_db_info_esp_test",
        description="test_db_desc_esp_test",
        type=ConnectionInfoTypes.DATABASE,
        params=database_info.model_dump())

    result : CreateConnectionInfo= await  connection_info_service.isConnect( connection_info , tenant_id=tenant_id)
    assert result is not None
    assert result.params is not None
    assert result.params["is_success"] is False