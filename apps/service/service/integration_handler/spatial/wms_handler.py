import json
from typing import Any
from fastapi.routing import APIRoute
from fastapi.requests import Request as FastapiRequest
from fastapi.responses import Response as FastapiResponse
from httpx import AsyncClient, BasicAuth
from pydantic import BaseModel, TypeAdapter
from mapa.core.data.query_args import QueryArgs
from mapa.gateway.connection_info.authentication_info_model import BasicAuthAuthenticationInfo
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo
from mapa.gateway.constant import AuthenticationInfoTypes
from mapa.gateway.integration.integration_model import SpatialConnection, SpatialExternalBackend, WmsServiceFormat
from service.integration_handler.integration_handler import IntegrationHandler
from service.integration_handler.spatial.transform_to_cql import TransformToCQL
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse
from owslib.wms import WebMapService

def dummy_endpoint_func(request: FastapiRequest) -> FastapiResponse:
    """ApiRoute için kullanılacak dummy response handler fonksiyonu"""
    return FastapiResponse()

class WmsRequest(BaseModel):
    service: str = "WMS"
    request: str = "GetMap"
    transparent: bool = False
    cql_filter: str = ""    
    format: str
    styles: str = ""
    layers: str
    width: int
    height: int
    box: str
    
class WmsRequest_1_1(WmsRequest):
    version: str = "1.1.1"
    srs: str = "EPSG:4326"
    
class WmsRequest_1_3(WmsRequest):
    version: str = "1.3.0"
    crs: str = "EPSG:4326"

class WmsHandler:
    def __init__(self, spatial_handler: IntegrationHandler) -> None:
        self.spatial_handler = spatial_handler
        self.transformer = TransformToCQL()
        
    async def execute(self, spatial_conn: SpatialConnection, service_request: ServiceRequest) -> ServiceResponse:
        
        # Authentication yapısı oluşturulur.
        conn_info: ConnectionInfo = self.spatial_handler.integration.connection_info  # type: ignore
        auth = self._create_auth(conn_info)
        
        # Backend bilgileri
        backend: SpatialExternalBackend = spatial_conn.backend  # type: ignore
        if not backend.endpoint.endswith("?"):
            backend.endpoint += "?" # add last char ? if not exist
            
        api_route = APIRoute(backend.endpoint, endpoint=dummy_endpoint_func, methods=[backend.method])
        url_path = api_route.url_path_for("dummy_endpoint_func", **(service_request.path_params or {}))
        client_params = {
            "timeout": self.spatial_handler.integration.timeout_in_millis,
            "verify": False,
            "follow_redirects": False
        }
        content: Any = self._create_content(service_request)
        query_args_str = service_request.query_params.get("query")
        if query_args_str:
            query_args = TypeAdapter(
                QueryArgs).validate_python(json.loads(query_args_str))
            service_request.query_params['cql_filter'] = self.transformer.transform(query_args)
            del service_request.query_params['query']

        # Format farkları
        if backend.service_format == WmsServiceFormat.WMS_1_1_1:
            service_request.query_params['version'] = '1.1.1'    
            if service_request.query_params.get('srs'):
                service_request.query_params['crs'] = service_request.query_params['srs']
                del service_request.query_params['srs']
        
        if backend.service_format == WmsServiceFormat.WMS_1_3_0:
            service_request.query_params['version'] = '1.3.0'    
        
        # Not : Wms Özelinde GetMap - GetCapabilities - GetStyles request Tipleri kullanılmaktadır.
        # Eğer GetStyles olarak gelen bir request varsa versionun bilgisinin 1.1.1 olması gerek
        request = service_request.query_params.get("request")
        if request == 'GetStyles':    
            service_request.query_params['version'] = '1.1.1' 
      
        # owslib test amaclı yapıldı  
        # if request == 'GetCapabilities': 
        #     url = SpatialExternalBackend(**spatial_conn.backend.model_dump()).endpoint
        #     vrsn = service_request.query_params['version']
        #     wms = WebMapService(url, version=vrsn)   
        #     service_response = ServiceResponse(
        #         status_code=200,
        #         response_type="application/json",
        #         # headers=dict(response.headers),
        #         body=wms
        #     ) 
        #     return service_response
            
        
        async with AsyncClient(**client_params) as client:
            request = client.build_request(
                service_request.method,
                url_path,
                # headers=service_request.headers,
                cookies=service_request.cookies,
                content=content,
                params=service_request.query_params
            )
            response = await client.send(request, auth=auth, follow_redirects=True)

        service_response = ServiceResponse(
            status_code=response.status_code,
            response_type=response.headers.get("content-type"),
            # headers=dict(response.headers),
            cookies=dict(response.cookies),
            body=response.read()
        )
        if service_response.response_type.find("application/json") > -1:
            service_response.body = json.loads(service_response.body) # type: ignore

        return service_response
        
    def _create_auth(self, connection_info: ConnectionInfo) -> Any:
        if connection_info and connection_info.params:
            # auth type BASICAUTH ise kimlik bilgileri döndürülür.
            if connection_info.params['type'] == AuthenticationInfoTypes.BASICAUTH:
                auth: BasicAuthAuthenticationInfo = connection_info.params['auth_params']
                return BasicAuth(**auth)  # type: ignore
            # Değilse kimlik bilgileri boş döndürülür
            else:
                return None
        return None
    
    def _create_content(self,req: Any):
        if req.headers.get("content-type") == 'application/xml':
            return req.body
      
        return json.dumps(req.body) if len(
                    req.body) > 0 else b""     