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
from mapa.gateway.integration.integration_model import SpatialBackendType, SpatialConnection, SpatialExternalBackend, TileServiceFormat
from service.integration_handler.integration_handler import IntegrationHandler
from service.integration_handler.spatial.transform_to_cql import TransformToCQL

from service.model.request import ServiceRequest
from service.model.response import ServiceResponse

def dummy_endpoint_func(request: FastapiRequest) -> FastapiResponse:
    """ApiRoute için kullanılacak dummy response handler fonksiyonu"""
    return FastapiResponse()


class TileHandler:
    format_dict = {
        "png": "image/png",
        "jpeg": "image/jpeg",
        "mvt": "application/vnd.mapbox-vector-tile"
    }

    def __init__(self, spatial_handler: IntegrationHandler) -> None:
        self.spatial_handler = spatial_handler
        self.transformer = TransformToCQL()
        
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

        url_path = ""
        backend: SpatialExternalBackend = spatial_conn.backend # type: ignore
        match backend.service_format:
            case TileServiceFormat.WMTS:
                url_path = self._create_wmts_url_path(backend, service_request)
            case TileServiceFormat.XYZ:
                url_path = self._create_xyz_url_path(backend, service_request)
            case TileServiceFormat.TMS:
                url_path = self._create_tms_url_path(backend, service_request)

        client_params = {
            "timeout": self.spatial_handler.integration.timeout_in_millis,
            "verify": False,
            "follow_redirects": False
        }
        content: Any = self._create_content(service_request)

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
    
    async def _execute_ad_hoc(self, spatial_conn: SpatialConnection, service_request: ServiceRequest) -> ServiceResponse:        
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

        backend.service_format

        query_args_str = service_request.query_params.get("query")
        # Default limit ve offset değerleri
        query_args = QueryArgs(limit=1000, offset=0)
        if query_args_str:
            query_args = TypeAdapter(
                QueryArgs).validate_python(json.loads(query_args_str))
            service_request.query_params["cql_filter"] = self.transformer.transform(query_args)
            del service_request.query_params["query"]

        # WFS parametreleri tamamlanır.
        service_request.query_params["service"] = "WFS"
        service_request.query_params["version"] = "2.0.0"
        service_request.query_params["request"] = "GetFeature"
        service_request.query_params["outputFormat"] = "application/json"
        service_request.query_params["count"] = query_args.limit
        service_request.query_params["startIndex"] = query_args.offset
        service_request.query_params["typeNames"] = service_request.query_params["typeName"]

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

    def _create_wmts_url_path(self, backend: SpatialExternalBackend, service_request: ServiceRequest) -> str:
        # TileMatrixSet ve Style parametreleri context, path ya da query parametresi olarak yazılabilir.
        tile_matrix_set = service_request.context.get('tilematrixset') or \
            service_request.path_params.get('tilematrixset') or \
            service_request.query_params.get('tilematrixset') or "EPSG:900913"
        style = service_request.context.get('style') or \
            service_request.path_params.get('style') or \
            service_request.query_params.get('style') or ""

        # Standart parametreler
        service = "WMTS"
        request = "GetTile"
        version = "1.0.0"

        # tile url /typename/z/x/y.format
        layer = service_request.path_params.get('typename') or ""
        ret_format = service_request.path_params.get('format') or ""
        # Changed by Bekir - mime_format = self.format_dict[ret_format] or "" 
        mime_format = "" if ret_format == "" else self.format_dict.get(ret_format, "")
        # Changed by Bekir - tile_matrix = f"{tile_matrix_set}:{service_request.path_params['z']}"
        tile_matrix = 0
        tile_col = 0
        tile_row = 0   
        if len(service_request.path_params) != 0:
            tile_matrix = f"{tile_matrix_set}:{service_request.path_params['z']}"
            tile_col = f"{service_request.path_params['x']}"
            tile_row = f"{service_request.path_params['y']}"
        
            return f"{backend.endpoint}?service={service}&request={request}&version={version}&style={style}" + \
                f"&layer={layer}&format={mime_format}&tilematrixset={tile_matrix_set}" + \
                f"&tilematrix={tile_matrix}&tilecol={tile_col}&tilerow={tile_row}"
        else:
            # http://localhost:33102/Admin/mapExtApi/wmtsRota?service=WMTS&request=GetCapabilities

            return f"{backend.endpoint}service={service}&request=GetCapabilities"

    def _create_xyz_url_path(self, backend: SpatialExternalBackend, service_request: ServiceRequest) -> str:
        api_route = APIRoute(backend.endpoint, endpoint=dummy_endpoint_func, methods=[backend.method])
        url_path = api_route.url_path_for("dummy_endpoint_func", **(service_request.path_params or {}))

        return url_path

    def _create_tms_url_path(self, backend: SpatialExternalBackend, service_request: ServiceRequest) -> str:
        api_route = APIRoute(backend.endpoint, endpoint=dummy_endpoint_func, methods=[backend.method])
        cp_params = service_request.path_params.copy()
        # TMS servisi için eksenin yönü değiştirilir.
        y = cp_params["y"]
        z = cp_params["z"]
        cp_params["y"] = (2^z) - y - 1
        url_path = api_route.url_path_for("dummy_endpoint_func", **(cp_params))

        return url_path
            
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