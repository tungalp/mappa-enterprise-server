import pytest
from mapa.gateway.soap.soap_service import SoapService
from .conftest import GatewayFixture, generate_integration_soap_test_qnb,generate_gateway_api, tenant_id,generate_authorization_info_test_qnb, generate_integration, generate_authorization_info, generate_integration_soap
from zeep import Client,xsd
from zeep.transports import Transport
from requests import Session
from typing import Any, Dict
from uuid import uuid4
from unittest.mock import Mock
from mapa.gateway.constant import ConnectionInfoTypes

from zeep.wsse.username import UsernameToken
from mapa.gateway.connection_info.authentication_info_model import BasicAuthAuthenticationInfo
from mapa.gateway.connection_info.connection_info_model import CreateConnectionInfo
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService

from mapa.gateway.gateway_api.gateway_api_model import GatewayApi, CreateGatewayApi, UpdateAllGatewayApi, UpdateGatewayApi
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService

from mapa.gateway.integration.integration_model import Integration, CreateIntegration, SoapConnection, UpdateAllIntegration, UpdateIntegration
from mapa.gateway.integration.integration_service import IntegrationService

from mapa.gateway.parameter_mapping.parameter_mapping_model import ParameterMapping, CreateParameterMapping, UpdateAllParameterMapping, UpdateParameterMapping
from mapa.gateway.parameter_mapping.parameter_mapping_service import ParameterMappingService

from mapa.gateway.route.route_model import Route, CreateRoute, UpdateAllRoute, UpdateRoute
from mapa.gateway.route.route_service import RouteService


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
        "route_service": route_service,
        "connection_info_service": connection_info_service,
    }
 
    
@pytest.mark.asyncio
async def test_create_services(fixture: GatewayFixture):
    """Service"""
    services = await create_services(fixture)
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    route_service: RouteService = services["route_service"]
    integration_service: IntegrationService = services["integration_service"]
    parameter_mapping_service: ParameterMappingService = services["parameter_mapping_service"]
    connection_info: ConnectionInfoService = services["connection_info_service"]

    assert connection_info is not None
    assert gateway_api_service is not None
    assert route_service is not None
    assert integration_service is not None
    assert parameter_mapping_service is not None    
    

async def create_service_soap(fixture: GatewayFixture) -> SoapService:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db = fixture.create_db_instance(fixture.db_url_async)

    return SoapService()

@pytest.mark.asyncio
async def test_create_service(fixture: GatewayFixture):
    """Service"""

    service: SoapService = await create_service_soap(fixture)
    assert service is not None

@pytest.mark.asyncio
async def test_soap_services_get_wsdl_infos(fixture: GatewayFixture):
    """Test"""
    
    services = await create_services(fixture)
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    integration_service: IntegrationService = services["integration_service"]  
    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    assert connection_info_service is not None

    assert gateway_api_service is not None
    assert integration_service is not None

    # https://pec.shaparak.ir/newipgservices/bill/billservice.asmx?WSDL
    # http://www.dneonline.com/calculator.asmx?WSDL
    # http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL
    # https://api.avangate.com/soap/6.0/?wsdl
    # https://apps.learnwebservices.com/services/tempconverter?wsdl
    endpoint = "https://erpefaturatest.cs.com.tr:8443/efatura/ws/connectorService?wsdl"

     # AuthorizationIfo
    auth_info = await connection_info_service.create(CreateConnectionInfo(
        name="test_auth_info_test_qnb",
        description="test_auth_info_desc_test_qnb",
        params=generate_authorization_info_test_qnb().dict(),
        type=ConnectionInfoTypes.AUTHENTICATION
    ), tenant_id=tenant_id)
    
    assert auth_info is not None
    assert auth_info.params is not None
    
    # Api oluşturulur
    create_gateway_api: CreateGatewayApi = generate_gateway_api()
    gateway_api: GatewayApi = await gateway_api_service.create(create_gateway_api, tenant_id)
    assert gateway_api is not None

    # Boş bir sorgulama yapılır
    empty_item = await integration_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None
    
    # Yeni test kayıtları oluşturulur
    integration_add = await (integration_service.create(generate_integration_soap_test_qnb(gateway_api.id,auth_info.id), tenant_id=tenant_id))
    assert integration_add is not None
    
    auth: BasicAuthAuthenticationInfo = auth_info.params['auth_params']
    wsse_auth =  UsernameToken(**auth)  # type: ignore
    soap = integration_add.connection 
    method = soap["method"]
    endpoint = soap["endpoint"]
    session = Session()
    session.verify = False
    session.trust_env = False
    client = Client(endpoint,transport=Transport(session=session),wsse=wsse_auth)
    
    parameters = []
    for input in soap["inputs"]:
        parameters.append(xsd.AnyObject(input['type'] , 4200081197 ))

    response = client.service[method](*[p.value for p in parameters])
    assert response is not None
    
    
@pytest.mark.asyncio
async def test_soap_services_calculator(fixture: GatewayFixture):
    """Test"""
    
    session = Session()
    session.verify = False
    session.trust_env = False
    client = Client("http://www.dneonline.com/calculator.asmx?WSDL",transport=Transport(session=session))
    response = client.service.Add(2,3)
    assert response == 5
    
    response = client.service.Divide(4,4)
    assert response == 1
     
    response = client.service.Multiply(4,1)
    assert response == 4
      
    response = client.service.Subtract(4,4)
    assert response == 0
    
@pytest.mark.asyncio
async def test_soap_services_CountryInfoService(fixture: GatewayFixture):
    """Test"""

    session = Session()
    session.verify = False
    session.trust_env = False
    client = Client("http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL",transport=Transport(session=session))
    response = client.service.ListOfContinentsByName()
    assert response is not None
 
@pytest.mark.asyncio
async def test_soap_services_manual_add(fixture: GatewayFixture):
    """Test"""
    
    services = await create_services(fixture)
    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    integration_service: IntegrationService = services["integration_service"]  
    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    assert connection_info_service is not None

    assert gateway_api_service is not None
    assert integration_service is not None

    # AuthorizationIfo
    auth_info = await connection_info_service.create(CreateConnectionInfo(
        name="test_auth_info3",
        description="test_auth_info_desc3",
        params=generate_authorization_info().dict(),
        type=ConnectionInfoTypes.AUTHENTICATION
    ), tenant_id=tenant_id)
    
    assert auth_info is not None
    assert auth_info.params is not None
    
    # Api oluşturulur
    create_gateway_api: CreateGatewayApi = generate_gateway_api()
    gateway_api: GatewayApi = await gateway_api_service.create(create_gateway_api, tenant_id)
    assert gateway_api is not None

    # Boş bir sorgulama yapılır
    empty_item = await integration_service.get(uuid4(), tenant_id=tenant_id)
    assert empty_item is None
    
    # Yeni test kayıtları oluşturulur
    integration_add = await (integration_service.create(generate_integration_soap(gateway_api.id,auth_info.id), tenant_id=tenant_id))
    assert integration_add is not None
    
    soap = integration_add.connection 
    method = soap["method"]
    endpoint = soap["endpoint"]
    session = Session()
    session.verify = False
    session.trust_env = False
    client = Client(endpoint,transport=Transport(session=session))
    
    parameters = []
    for input in soap["inputs"]:
        parameters.append(xsd.AnyObject(input['type'] , 2 ))

    response = client.service[method](*[p.value for p in parameters])
    assert response == 4
