from uuid import UUID, uuid4
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import  FilterOp, QueryArgs,Filter
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService
from mapa.gateway.constant import IntegrationTypes, MethodTypes
from mapa.gateway.integration.integration_model import CreateIntegration, SpatialConnection, SpatialServiceType, UpdateAllIntegration, UpdateIntegration, Integration
from mapa.gateway.integration.integration_repository import IntegrationRepository
from mapa.gateway.route.route_model import CreateRoute,Route
from typing import Any, Dict, List
from mapa.core.data.base_service import BaseService
import operator
from functools import lru_cache
from lxml import etree
from mapa.core.data.result import PagingResult
from mapa.gateway.connection_info.authentication_info_model import BasicAuthAuthenticationInfo
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo
from mapa.gateway.constant import AuthenticationInfoTypes
from mapa.gateway.integration.integration_model import SoapConnection
from mapa.gateway.route.route_service import RouteService
from mapa.gateway.soap.soap_model import SoapBindingModel, SoapInputModel, SoapMethodModel, SoapModel, SoapServiceModel
from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client, Settings, AsyncClient
from zeep.transports import Transport 
from zeep.wsse.username import UsernameToken
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from zeep.xsd.types import ComplexType
from zeep.xsd.types.any import AnyType
from zeep.xsd.types.simple import AnySimpleType
import requests_cache

requests_cache.install_cache('zeep_cache', expire_after=86400)

class IntegrationService(BaseEntityService[IntegrationRepository, Integration, CreateIntegration, UpdateIntegration, UpdateAllIntegration]):
    """Integration Servisi"""

    def __init__(self, async_db: AsyncDatabase,
                 route_service: RouteService,
                 connection_info_service:ConnectionInfoService) -> None:
        self.async_db = async_db
        self._route_service = route_service
        self._connection_info_service = connection_info_service
        super().__init__(async_db, IntegrationRepository, Integration)
        
        
    async def create(self, integration: CreateIntegration, tenant_id: str | None = None) -> Integration:
        """integration oluştururken default route seceneği işaretli ise tanımlı olan GET-POST-PUT-DELETE route kayıtları da oluşturulur"""
        
        created_integration = None
        created_route = None
        try:
            created_integration = await super().create(integration, tenant_id)
        
            if integration.default_route:
                routes = generate_default_routes(integration,created_integration.id)
                if len(routes) > 0:
                    created_route = await self._route_service.create_all(routes, tenant_id)
        except Exception as Ex:
            if created_route is not None and created_route.id is not None:
                await self._route_service.delete(created_route.id, tenant_id) 
            if created_integration is not None and created_integration.id is not None:
                await super().delete(created_integration.id, tenant_id)
            raise Ex

        return created_integration

    async def create_all(self, integrations: List[CreateIntegration], tenant_id: str | None = None) -> List[Integration]:
        """integration oluştururken default route seceneği işaretli ise tanımlı olan GET-POST-PUT-DELETE route kayıtları da oluşturulur"""
        created_integrations = []
        try:
            for integration in integrations:
               created_integrations.append(await self.create(integration, tenant_id))
        except Exception as Ex:
            raise Ex
        
        return created_integrations
    
    
    async def get_soap_infos(self, tenant_id:str, soap_wsdl_endpoint: str, soap_endpoint: str | None = None, connection_info_id: str | None = None) -> List[SoapModel]:
        """Soap servisinin Servislerini, methodlarını ve inputlarını döner"""
        
        auth = None
        if connection_info_id:
            query_connection: QueryArgs = QueryArgs(where=[
                Filter(field="id", op=FilterOp.EQUAL, value=connection_info_id)], limit=0, offset=0)
            connection_info: PagingResult[ConnectionInfo] = await self._connection_info_service.paging(query_connection, tenant_id) 
            # Authentication yapısı oluşturulur.
            if connection_info and connection_info.items and len(connection_info.items)>0:
                auth = await self.create_auth(connection_info.items[0])
        
        # Backend bilgileri
        client = await self.create_soap_client(soap_wsdl_endpoint,auth)
        print('soap_wsdl_endpoint:', soap_wsdl_endpoint ,' servisine bağlandı.')
        print('soap_endpoint:', soap_endpoint ,' servisine bağlandı.')
        print('client:', client)
        wsld_list: List[SoapModel] = []
        soap = Any   # type: ignore  
        
        try:
            for service in client.wsdl.services.values():
                print('service:', str(service))
                soap : SoapModel = SoapModel(services=SoapServiceModel(service_name=service.name,bindings={}).dict())
                binding_list : List[SoapBindingModel] = []
                for port in service.ports.values():
                    print('port:', str(port))
                    operations = sorted(
                        port.binding._operations.values(),
                        key=operator.attrgetter('name'))
                    binding : SoapBindingModel = SoapBindingModel(binding_name=port.name,methods={})
                    method_list : Any = []
                    print('operations:', str(operations))
                    for operation in operations:                        
                        input_list = []
                        
                        try:
                            if (operation.input is not None and 
                                operation.input.body is not None and 
                                operation.input.body.type is not None and 
                                operation.input.body.type.elements is not None and 
                                operation.name is not None):
                                print('operation:', str(operation))
                                print('operation.input:', str(operation.input))
                                elements = operation.input.body.type.elements
                                input_list = parse_elements(elements)
                                method_list.append(SoapMethodModel(method_name=operation.name,inputs = input_list))
                        except Exception as ex:
                            print(str(ex))
                                   
                    binding.methods = method_list
                    binding_list.append(binding)
                soap.services['bindings'] = binding_list
            wsld_list.append(soap)    
        except Exception as ex:
            raise ex    
    
        return wsld_list

    
    async def create_soap_client(self, wsdl_endpoint: str, wsse_auth : UsernameToken | None = None) -> AsyncClient:
        """Verilen wsdl_endpoint bilgisine göre zeep Client oluşturur."""
        settings = {
            "force_https":False,
            "strict":False
        }
        session = Session()
        session.verify = False
        session.trust_env = False
        # bu yazılmadığı zaman 300 sn kitleniyor servis, şimdilik sabit, (02.07.24)
        timeout=10
        if wsse_auth:
            session.auth = HTTPBasicAuth(wsse_auth.username, wsse_auth.password) # type: ignore  
            return AsyncClient(wsdl_endpoint, settings=Settings(**settings),transport=Transport(session=session,timeout=timeout,operation_timeout=timeout), wsse=wsse_auth)
        return AsyncClient(wsdl_endpoint, settings=Settings(**settings),transport=Transport(session=session,timeout=timeout,operation_timeout=timeout))


    # Soap wsse-securty için UsernameToken olarak döndürülmüştür.
    async def create_auth(self, connection_info: ConnectionInfo) -> Any:
        if connection_info and connection_info.params:
            # auth type BASICAUTH ise kimlik bilgileri döndürülür.
            if connection_info.params['type'] == AuthenticationInfoTypes.BASICAUTH:
                auth: BasicAuthAuthenticationInfo = connection_info.params['auth_params']
                return UsernameToken(**auth)  # type: ignore  
                # Değilse kimlik bilgileri boş döndürülür
            else:
                return None
        return None



def parse_elements(elements):
    input_list = []
    print('elements:',str(elements))
    for name, element in elements:
        print('name:',str(name))
        print('element:',str(element))

        model : SoapInputModel = SoapInputModel(name= "",type= "", optional= False, params = [])
        model.optional = element.is_optional
        
        if element.name is not None:
            model.name = str(element.name)
        else:
            model.name = name
        
        # Eğer element tipi ComplexType ise, complex tip olarak kabul edilir
        if isinstance(element.type, ComplexType):
            model.params = parse_elements(element.type.elements)
            model.type = 'Object'
        # Eğer element tipi SimpleType ise, primitive tip olarak kabul edilir
        elif isinstance(element.type, AnySimpleType):
            model.type = element.type.name
            model.params = []
        # Eğer elementin tipi 'AnyType' ise, genel bir veri tipi olduğu kabul ediliyor
        elif isinstance(element.type, AnyType):
            model.type = 'Any'
            model.params = []  # AnyType olduğunda alt eleman olmadığını varsayıyoruz
        else:
            # Eğer başka bir tipe sahipse, default olarak tipini alır
            model.type = element.type.name
            model.params = []
            
        input_list.append(model) 
    return input_list


def generate_default_routes(integration: CreateIntegration, created_integration_id: UUID):    
    routes = []
    default_methods = integration.default_route_methods if integration.default_route_methods else []
    if integration.type == IntegrationTypes.SPATIAL_BACKEND:
        spatial_conn = SpatialConnection(**integration.connection)
        match spatial_conn.service_type:
            case SpatialServiceType.WMS | SpatialServiceType.Feature | SpatialServiceType.Tile:
                if "GET" in default_methods:
                    routes.append(CreateRoute(
                        method_type=MethodTypes.GET,
                        path=str(integration.default_route_path),
                        gateway_api_id=integration.gateway_api_id,
                        integration_id=created_integration_id,
                        description=f"{integration.description} (GET)" if integration.description else "(GET)"
                    ))
            case SpatialServiceType.Transaction:
                for method in ["POST", "PUT", "DELETE"]:
                    if method in default_methods:
                        routes.append(CreateRoute(
                            method_type=getattr(MethodTypes, method),
                            path=str(integration.default_route_path),
                            gateway_api_id=integration.gateway_api_id,
                            integration_id=created_integration_id,
                            description=f"{integration.description} ({method})" if integration.description else f"({method})"
                        ))
    else:
        for method in default_methods:
            routes.append(CreateRoute(
                method_type=getattr(MethodTypes, method),
                path=str(integration.default_route_path),
                gateway_api_id=integration.gateway_api_id,
                integration_id=created_integration_id,
                description=f"{integration.description} ({method})" if integration.description else f"({method})"
            ))

    return routes
