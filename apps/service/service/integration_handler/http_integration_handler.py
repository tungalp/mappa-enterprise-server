from typing import Any
from fastapi.requests import Request as FastapiRequest
from fastapi.responses import Response as FastapiResponse
from fastapi.routing import APIRoute
from httpx import AsyncClient, Request, BasicAuth
from mapa.gateway.connection_info.authentication_info_model import (
    AuthenticationInfo,
    BasicAuthAuthenticationInfo,
)
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo
from mapa.gateway.constant import AuthenticationInfoTypes, MethodTypes
from mapa.gateway.integration.integration_model import HttpBackendConnection
from service.integration_handler.integration_handler import IntegrationHandler
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse
import json


def dummy_endpoint_func(request: FastapiRequest) -> FastapiResponse:
    """ApiRoute için kullanılacak dummy response handler fonksiyonu"""
    return FastapiResponse()


def auth_func(request: Request) -> Request:
    return request


class HttpIntegrationHandler(IntegrationHandler):
    """Http İsteklerini karşılayan entegrasyon sınıfı"""

    async def execute(self, service_request: ServiceRequest) -> ServiceResponse:
        if not self.integration.connection:
            raise ValueError("Connection not defined")

        # Authentication yapısı oluşturulur.
        conn_info: ConnectionInfo = self.integration.connection_info  # type: ignore
        auth = self._create_auth(conn_info)

        # Backend bilgileri
        http_conn = HttpBackendConnection(**(self.integration.connection))
        api_route = APIRoute(
            http_conn.endpoint,
            endpoint=dummy_endpoint_func,
            methods=[service_request.method],
        )
        url_path = api_route.url_path_for(
            "dummy_endpoint_func", **(service_request.path_params or {})
        )
        timeout = (
            (self.integration.timeout_in_millis / 1000)
            if self.integration.timeout_in_millis is not None
            and (self.integration.timeout_in_millis / 1000) != 0
            else 10
        )
        client_params = {"timeout": timeout, "verify": False, "follow_redirects": True}
        print(str(service_request))
        content: Any = self._create_content(service_request)
        headers = self._build_headers(service_request.headers)

        async with AsyncClient(**client_params) as client:
            request = client.build_request(
                (
                    service_request.method
                    if http_conn.method == MethodTypes.ANY
                    else http_conn.method
                ),
                url_path,
                headers=headers,
                cookies=service_request.cookies,
                content=content,
                params=service_request.query_params,
            )
            response = await client.send(request, auth=auth, follow_redirects=True)
        
        body = await response.aread()
        service_response = ServiceResponse(
            status_code=response.status_code,
            response_type=response.headers.get("content-type"),
            # headers=dict(response.headers),
            cookies=dict(response.cookies),
            body=body,
        )
        if service_response.response_type.find("application/json") > -1:
            service_response.body = (
                json.loads(service_response.body.decode("utf-8")) if len(service_response.body) > 0 else ""  # type: ignore
            )

        return service_response

    def _create_auth(self, connection_info: ConnectionInfo) -> Any:
        if connection_info and connection_info.params:
            # auth type BASICAUTH ise kimlik bilgileri döndürülür.
            if connection_info.params["type"] == AuthenticationInfoTypes.BASICAUTH:
                auth: BasicAuthAuthenticationInfo = connection_info.params[
                    "auth_params"
                ]
                return BasicAuth(**auth)  # type: ignore
            # Değilse kimlik bilgileri boş döndürülür
            else:
                return None
        return None

    # Not : Content Type Xml gelen bodyler doğrudan aktarılmıştır. (27.09.2023)
    def _create_content(self, req: Any):
        if req.headers.get("content-type") == "application/xml":
            return req.body

        return json.dumps(req.body) if len(req.body) > 0 else b""

    # Not : Şimdilik sadece headers içerisindeki content-type bilgisi doldurulmaktadır. (10.10.2023)
    def _build_headers(self, req_headers: Any):
        headers = {}
        if req_headers.get("content-type") is not None:
            headers["Content-Type"] = req_headers.get("content-type")

        if req_headers.get("tenant_id") is not None:
            headers["X-Tenant-ID"] = req_headers.get("tenant_id")

        if req_headers.get("user_id") is not None:
            headers["X-User-ID"] = req_headers.get("user_id")

        if req_headers.get("Authorization") is not None:
            headers["X-Forwarded-Token"] = req_headers.get("Authorization")

        return headers
