from typing import List
import pytest
import asyncio
from nanoid import generate
from uuid import UUID, uuid4

from sqlalchemy import text
from mapa.gateway.connection_info.authentication_info_model import BasicAuthAuthenticationInfo, CreateAuthenticationInfo
from mapa.gateway.connection_info.database_info_model import CreateDatabaseInfo, DatabaseInfo
from mapa.gateway.context_var.context_var_model import CreateConvextVar
from mapa.gateway.integration.integration_model import CreateIntegration, HttpBackendConnection, SoapConnection
from mapa.gateway.parameter_mapping.parameter_mapping_model import CreateRequestResponseMapping, CreateParameterMapping
from mapa.test.base_fixture import BaseFixture
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi
from mapa.gateway.route.route_model import CreateRoute
from mapa.gateway.constant import ValueTypes, ModifierTypes, ParameterTypes, ValueTypes, ModifierTypes, ParameterTypes, ApiTypes, IntegrationTypes, MethodTypes, AuthenticationInfoTypes, ParameterMappingTypes
from mapa.gateway.soap.soap_model import SoapInputModel
from .data_spatial import instances

tenant_id = "10a2238f-4d1e-4626-9f3c-799d3ef5e96d"


class GatewayFixture(BaseFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False
        self.config = {
            "api_host": "http://0.0.0.0:33101",
            "app_host": "http://0.0.0.0:33001",
            "secret": "top_secret"
        }

    async def create_test_data(self) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        if self.__test_data_created:
            return True

        async_db = self.create_db_instance(self.db_url_async_init)

        initialized = await self.create_database(async_db)
        self.__test_data_created = True

        if initialized:
            await self.grant_permissions(async_db, "mapa_test", "mapa", "gateway")
            await self.grant_permissions(async_db, "mapa_test", "mapa", "manage")
            try:
                self.__test_data_created = await self.create_data(async_db, instances)
            except Exception as ex:
                print("Spatial test verilerinin oluşturulmasında hata oluştu.", ex)

        return initialized

@pytest.fixture(scope="session")
def event_loop():
    """Async test metodları için default event loop"""

    try:
        loop = asyncio.get_running_loop()
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def fixture(event_loop) -> GatewayFixture:  # type: ignore
    """Oturum bazlı fikstür parametresi_
    """
    yield GatewayFixture()  # type: ignore


def generate_gateway_api() -> CreateGatewayApi:
    return CreateGatewayApi(description="Test desc"+generate(size=4),
                            name="Test api"+generate(size=4),
                            type=ApiTypes.HTTP,
                            path="Testapipath"+generate(size=4),
                            identifier="identfier"+generate(size=4),
                            context=dict({
                                "x-ibm-client-id": "client-id-test",
                                "x-ibm-client-secret": "client-secret",
                                "secret": {
                                    "username": "test",
                                    "password": "test-password",
                                    "loginCount": 123
                                }
                            }))


def generate_integration(gateway_api_id: UUID = uuid4(), connection_info_id: UUID = uuid4()) -> CreateIntegration:
    return CreateIntegration(description="Test integration desc"+generate(size=4),
                             name="Test integration"+generate(size=4),
                             type=IntegrationTypes.HTTP_BACKEND,
                             gateway_api_id=gateway_api_id,
                             connection_info_id=connection_info_id,
                             connection=HttpBackendConnection(method="GET", endpoint="p1").dict(),
                             default_route= False,
                             default_route_path= " ",
                             default_route_methods = [],
                             context={})


def generate_integration_soap(gateway_api_id: UUID = uuid4(), connection_info_id: UUID = uuid4()) -> CreateIntegration:
    return CreateIntegration(description="Test integration desc"+generate(size=4),
                             name="Test integration"+generate(size=4),
                             type=IntegrationTypes.SOAP_BACKEND,
                             gateway_api_id=gateway_api_id,
                             connection_info_id=connection_info_id,
                             connection=generate_soap_modal().dict(),
                             default_route= False,
                             default_route_path= " ",
                             default_route_methods = [],
                             context={})
    
def generate_integration_soap_test_qnb(gateway_api_id: UUID = uuid4(), connection_info_id: UUID = uuid4()) -> CreateIntegration:
    return CreateIntegration(description="Test integration desc"+generate(size=4),
                             name="Test integration"+generate(size=4),
                             type=IntegrationTypes.SOAP_BACKEND,
                             gateway_api_id=gateway_api_id,
                             connection_info_id=connection_info_id,
                             connection=generate_soap_modal().dict(),
                             default_route= False,
                             default_route_path= " ",
                             default_route_methods = [],
                             context={})


def generate_soap_modal() -> SoapConnection:
    return SoapConnection(
        method="efaturaKullaniciBilgisi", wsdl_endpoint="https://erpefaturatest.cs.com.tr:8443/efatura/ws/connectorService?wsdl", endpoint="https://erpefaturatest.cs.com.tr:8443/efatura/ws/connectorService?wsdl", inputs=[SoapInputModel(name="vergiTcKimlikNo",optional=True,type="String(value)")] )


def generate_route(gateway_api_id: UUID = uuid4()) -> CreateRoute:
    return CreateRoute(description="Test route desc"+generate(size=4),
                       path="/Testpath/"+generate(size=4),
                       method_type=MethodTypes.GET,
                       query="?id={id}",
                       gateway_api_id=gateway_api_id)


def generate_authorization_info() -> CreateAuthenticationInfo:
    return CreateAuthenticationInfo(
        type=AuthenticationInfoTypes.BASICAUTH,
        auth_params=BasicAuthAuthenticationInfo(username="u1", password="p1"))
    
def generate_authorization_info_test_qnb() -> CreateAuthenticationInfo:
    return CreateAuthenticationInfo(
        type=AuthenticationInfoTypes.BASICAUTH,
        auth_params=BasicAuthAuthenticationInfo(username="4200081197", password="123qweoO"))   


def generate_database_info_esp_test() -> CreateDatabaseInfo:
    return CreateDatabaseInfo(
        dialect="postgresql",
        username="mapa",
        password="12345Abc.",
        host="db",
        port=5432,
        database="mapa_test",)


def generate_database_info_kdi_merkez() -> CreateDatabaseInfo:
    return CreateDatabaseInfo(
        dialect="postgresql",
        username="postgres",
        password="12345Abc.",
        host="db",
        port=5432,
        database="mapa_test",)


def generate_database_info_islem_oracle() -> DatabaseInfo:
    return DatabaseInfo(
        dialect="oracle+cx_oracle",
        username="INSTALLER",
        password="INSTALLER12345Abc.",
        host="db",
        port=1521,
        database="DEV")


def generate_database_info() -> CreateDatabaseInfo:
    return CreateDatabaseInfo(
        dialect="oracle",
        username="scott",
        password="tiger",
        host="127.0.0.1",
        port=8800,
        database="sidname",)


def generate_request_parameter_mapping(status_code: int, integration_id: UUID = uuid4()) -> CreateParameterMapping:
    return CreateParameterMapping(
        status_code=status_code,
        type=ParameterMappingTypes.REQUEST,
        param_list=[
            CreateRequestResponseMapping(
                parameter_type=ParameterTypes.HEADER,
                parameter="token",
                modifier=ModifierTypes.APPEND,
                value_type=ValueTypes.HEADER,
                value="id").dict(),

            CreateRequestResponseMapping(
                parameter_type=ParameterTypes.BODY,
                parameter=ParameterTypes.BODY,
                modifier=ModifierTypes.OVERWRITE,
                value_type=ValueTypes.STATIC,
                value="4400").dict()
        ],
        integration_id=integration_id,)


def generate_response_parameter_mapping(status_code: int, integration_id: UUID = uuid4()) -> CreateParameterMapping:
    return CreateParameterMapping(
        status_code=status_code,
        type=ParameterMappingTypes.RESPONSE,
        param_list=[
            CreateRequestResponseMapping(
                parameter_type=ParameterTypes.HEADER,
                parameter="token",
                modifier=ModifierTypes.APPEND,
                value_type=ValueTypes.HEADER,
                value="id").dict(),

            CreateRequestResponseMapping(
                parameter_type=ParameterTypes.BODY,
                parameter=ParameterTypes.BODY,
                modifier=ModifierTypes.OVERWRITE,
                value_type=ValueTypes.STATIC,
                value="4400").dict()
        ],
        integration_id=integration_id,)


def generate_route_list(gateway_api_id: UUID = uuid4()) -> List[CreateRoute]:
    return [CreateRoute(description="Test route desc"+generate(size=4),
                        path="/Testpath/" +
                        generate(size=4)+"?parselNo={parselNo}",
                        method_type=MethodTypes.GET,
                        gateway_api_id=gateway_api_id),
            CreateRoute(description="Test route desc"+generate(size=4),
                        path="/Testpath/" +
                        generate(
                            size=4)+"?parselNo={parselNo}"+'&'+"parselAd={parselAd}",
                        method_type=MethodTypes.GET,
                        gateway_api_id=gateway_api_id),
            CreateRoute(description="Test route desc"+generate(size=4),
                        path="/Testpath/"+generate(size=4)+"/path"+generate(
                            size=4)+""+"?parselNo={parselNo}"+'&'+"parselAd={parselAd}",
                        method_type=MethodTypes.GET,
                        gateway_api_id=gateway_api_id),
            CreateRoute(description="Test route desc"+generate(size=4),
                        path="/Testpath/"+generate(size=4)+"/path"+generate(
                            size=4)+"/"+"{parsel}"+"?parselNo={parselNo}"+'&'+"parselAd={parselAd}",
                        method_type=MethodTypes.GET,
                        gateway_api_id=gateway_api_id),
            CreateRoute(description="Test route desc"+generate(size=4),
                        path="/Testpath/" +
                        generate(size=4)+"/{role}/{user}/{id}",
                        method_type=MethodTypes.GET,
                        gateway_api_id=gateway_api_id),
            CreateRoute(description="Test route desc"+generate(size=4),
                        path="/Testpath/" +
                        generate(size=4)+"/{role}/{user}/{id}" +
                        "?validate={validatevalue}",
                        method_type=MethodTypes.GET,
                        gateway_api_id=gateway_api_id),
            CreateRoute(description="Test route desc"+generate(size=4),
                        path="/Testpath"+generate(size=4),
                        method_type=MethodTypes.GET,
                        gateway_api_id=gateway_api_id)]


def generate_context_var() -> CreateConvextVar:
    return CreateConvextVar(
        key=f"key_{generate(size=4)}",
        value=f"value_{generate(size=4)}"
    )


def generate_context_var2() -> CreateConvextVar:
    return CreateConvextVar(
        key=f"key_{generate(size=4)}",
        value={
            "value": f"{generate(size=4)}",
            "value2": f"{generate(size=4)}"
        }
    )
