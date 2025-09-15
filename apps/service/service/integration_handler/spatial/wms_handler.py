import json
import time
from typing import Any
from fastapi.routing import APIRoute
from fastapi.requests import Request as FastapiRequest
from fastapi.responses import Response as FastapiResponse
from httpx import AsyncClient, BasicAuth, Timeout
import httpx
import orjson
from pydantic import BaseModel, TypeAdapter
from mapa.core.data.query_args import QueryArgs
from mapa.gateway.connection_info.authentication_info_model import BasicAuthAuthenticationInfo
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo
from mapa.gateway.constant import AuthenticationInfoTypes
from mapa.gateway.integration.integration_model import SpatialConnection, SpatialExternalBackend, WmsServiceFormat
from service.http_client.http_client import get_global_client
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
        start_time = time.time()

        try:
            client = await get_global_client()

            # Authentication yapısı oluşturulur.
            conn_info: ConnectionInfo = self.spatial_handler.integration.connection_info  # type: ignore
            auth = self._create_auth(conn_info)
            
            # Backend bilgileri
            backend: SpatialExternalBackend = spatial_conn.backend  # type: ignore
            if not backend.endpoint.endswith("?"):
                backend.endpoint += "?" # add last char ? if not exist
                
            api_route = APIRoute(backend.endpoint, endpoint=dummy_endpoint_func, methods=[backend.method])
            url_path = api_route.url_path_for("dummy_endpoint_func", **(service_request.path_params or {}))

            content: Any = self._create_content(service_request)
            query_args_str = service_request.query_params.get("query")
            if query_args_str:
                query_args = TypeAdapter(
                    QueryArgs).validate_python(orjson.loads(query_args_str))
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

            request = client.build_request(
                service_request.method,
                url_path,
                # headers=service_request.headers,
                cookies=service_request.cookies,
                content=content,
                params=service_request.query_params
            )
            response = await client.send(request, auth=auth, follow_redirects=True)

            # Response işleme
            response_body = response.content
            response_type = response.headers.get("content-type", "")
            
            # JSON parsing
            if response_type and "application/json" in response_type:
                try:
                    response_body = orjson.loads(response_body)
                except orjson.JSONDecodeError:
                    try:
                        response_body = json.loads(response_body.decode('utf-8'))
                    except:
                        response_body = response_body
            
            service_response = ServiceResponse(
                status_code=response.status_code,
                response_type=response_type,
                cookies=dict(response.cookies),
                body=response_body
            )
            
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000
            print(f"WMS request completed in {processing_time:.2f}ms")
            
            return service_response
        except Exception as e:
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000
            print(f"WMS request failed after {processing_time:.2f}ms: {e}")
            raise e
        
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