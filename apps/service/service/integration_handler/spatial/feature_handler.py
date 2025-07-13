import json
from typing import Any
import xml.etree.ElementTree as ET
from fastapi.routing import APIRoute
from fastapi.requests import Request as FastapiRequest
from fastapi.responses import Response as FastapiResponse
from httpx import AsyncClient, BasicAuth
from pydantic import BaseModel, TypeAdapter
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.gateway.connection_info.authentication_info_model import BasicAuthAuthenticationInfo
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo
from mapa.gateway.constant import AuthenticationInfoTypes
from mapa.gateway.integration.integration_model import SpatialAdhocBackend, SpatialBackendType, SpatialConnection, SpatialExternalBackend, WmsServiceFormat
from service.integration_handler.integration_handler import IntegrationHandler
from service.integration_handler.spatial.transform_to_cql import TransformToCQL
from service.integration_handler.spatial.transform_to_ogc import TransformToOGC
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse
from mapa.gateway.integration.integration_model import SpatialServerType

from lxml import etree

def dummy_endpoint_func(request: FastapiRequest) -> FastapiResponse:
    """ApiRoute için kullanılacak dummy response handler fonksiyonu"""
    return FastapiResponse()

class FeatureHandler:
    def __init__(self, spatial_handler: IntegrationHandler) -> None:
        self.spatial_handler = spatial_handler
        self.transformer = TransformToCQL()
        self.transformerOGC = TransformToOGC()
        
    async def execute(self, spatial_conn: SpatialConnection, service_request: ServiceRequest) -> ServiceResponse:
       
        # Backend bilgileri
        backend_type = spatial_conn.backend.type
        if backend_type == SpatialBackendType.External:
            return await self._execute_external(spatial_conn, service_request)
        else:
            return await self._execute_ad_hoc(spatial_conn, service_request)
        

    async def _execute_external(self, spatial_conn: SpatialConnection, service_request: ServiceRequest) -> ServiceResponse:
        # Authentication yapısı oluşturulur.
        conn_info: ConnectionInfo = self.spatial_handler.integration.connection_info  # type: ignore
        auth = self._create_auth(conn_info)
        
        backend: SpatialExternalBackend = spatial_conn.backend # type: ignore
        api_route = APIRoute(backend.endpoint, endpoint=dummy_endpoint_func, methods=[backend.method])
        url_path = api_route.url_path_for("dummy_endpoint_func", **(service_request.path_params or {}))
        client_params = {
            "timeout": self.spatial_handler.integration.timeout_in_millis,
            "verify": False,
            "follow_redirects": False
        }
        content: Any = self._create_content(service_request)
        query_args_str = service_request.query_params.get("query")
        
        server_type = SpatialServerType.Geoserver            
        if "wmsServerType" in service_request.query_params and service_request.query_params["wmsServerType"] == SpatialServerType.ArcGIS:
            server_type = SpatialServerType.ArcGIS
            del service_request.query_params["wmsServerType"] 
        
        # Default limit ve offset değerleri
        query_args = QueryArgs(limit=1000, offset=0)
        if query_args_str:
            query_args = TypeAdapter(
                QueryArgs).validate_python(json.loads(query_args_str))
            # targetProj Transform edilecek SRID bilgisidir. Clientdan gelmektedir. (18.04.2024)
            target_proj = service_request.query_params["targetProj"]
            
            if server_type == SpatialServerType.Geoserver:
                service_request.query_params["cql_filter"] = self.transformer.transform(query_args, target_proj)
            else:
                filter = self.transformerOGC.transform(query_args, target_proj)
                service_request.query_params["filter"] = etree.tostring(filter)
                service_request.query_params["filter"] = service_request.query_params["filter"].decode('utf-8') 
            
            if "cql_filter" in service_request.query_params and service_request.query_params["cql_filter"] == '':
                del service_request.query_params["cql_filter"]
                
            if "filter" in service_request.query_params and service_request.query_params["filter"] == '':
                del service_request.query_params["filter"] 
                
            if "targetProj" in service_request.query_params and service_request.query_params["targetProj"] == '':
                del service_request.query_params["targetProj"] 
    
            if "query" in service_request.query_params and service_request.query_params["query"] == '':
                del service_request.query_params["query"]      
                
        
        # Not : request bilgisi DescribeFeatureType dikkate alınarak iki ayrı işleme çevrilebilir. (7.11.2023) 
        # WFS parametreleri tamamlanır.
        if service_request.query_params.get("request") is None:
            service_request.query_params["service"] = "WFS"
            service_request.query_params["version"] = "2.0.0"
            service_request.query_params["request"] = "GetFeature"
            service_request.query_params["outputFormat"] = "application/json"
            service_request.query_params["count"] = query_args.limit
            service_request.query_params["startIndex"] = query_args.offset
            service_request.query_params["typeNames"] = service_request.query_params["typeName"]
            
            del service_request.query_params["typeName"]
            
            if server_type == SpatialServerType.ArcGIS:
                service_request.query_params["outputFormat"] = "GEOJSON"
            
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
        
        # Not : FeatureHandler işlemlerinde dönüş bilgisinin PagingResult olması gerek (29.11.2023)
        # TODO : düzenleme isteyebilir (29.11.2023)
        
        if service_response.response_type.find("application/json") > -1:
            service_response.body = json.loads(service_response.body) # type: ignore
            
            # server_type bilgisine göre ayrılmak zorunda kaldı. application/json bilgisi arcgis'in GetFeature servisinin outputFormat'larında yok.
            # Bundan dolayıda sorgular ilk önce GEOJSON olarak sorgulandı ve totalCount'u da almak için resultType=hits ve outputFormat=GML32 paramsları eklendi.
            # 26.06.2024
            
            if server_type == SpatialServerType.Geoserver:
                if service_response.body['features']:
                    service_response.body = PagingResult(total=service_response.body["numberMatched"], items=service_response.body['features'],offset=query_args.offset, limit=query_args.limit).model_dump_json()
                else:
                    service_response.body = PagingResult(total= 0, items=[],offset=query_args.offset, limit=query_args.limit).model_dump_json()

            if server_type == SpatialServerType.ArcGIS:
                if service_response.body['features']:
                    
                    service_request.query_params["resultType"] = "hits"
                    service_request.query_params["outputFormat"] = "GML32"
                    
                    async with AsyncClient(**client_params) as client:
                        request_count = client.build_request(
                            service_request.method,
                            url_path,
                            # headers=service_request.headers,
                            cookies=service_request.cookies,
                            content=content,
                            params=service_request.query_params
                        )
                        response_count = await client.send(request_count, auth=auth, follow_redirects=True)
                    
                    root = ET.fromstring(response_count.content)
                    number_matched = root.attrib.get('numberMatched',None)
                    service_response.body = PagingResult(total=int(number_matched or 0) , items=service_response.body['features'],offset=query_args.offset, limit=query_args.limit).model_dump_json()
                else:
                    service_response.body = PagingResult(total= 0, items=[],offset=query_args.offset, limit=query_args.limit).model_dump_json()
        
            service_response.body = json.loads(service_response.body) if len(service_response.body) > 0 else "" # type: ignore

        return service_response
    
    async def _execute_ad_hoc(self, spatial_conn: SpatialConnection, service_request: ServiceRequest) -> ServiceResponse:        
        ...
        
    def _create_auth(self, connection_info: ConnectionInfo) -> Any:
        if connection_info and connection_info.params:
            # auth type BASICAUTH ise kimlik bilgileri döndürülür.
            if connection_info.params["type"] == AuthenticationInfoTypes.BASICAUTH:
                auth: BasicAuthAuthenticationInfo = connection_info.params["auth_params"]
                return BasicAuth(**auth)  # type: ignore
            # Değilse kimlik bilgileri boş döndürülür
            else:
                return None
        return None
    
    def _create_content(self,req: Any):
        if req.headers.get("content-type") == "application/xml":
            return req.body
      
        return json.dumps(req.body) if len(
                    req.body) > 0 else b""     