from typing import Any, Dict
from fastapi.requests import Request as FastapiResuest
from fastapi.responses import Response as FastapiResponse
from fastapi.routing import APIRoute
from httpx import AsyncClient, Request, BasicAuth
from mapa.gateway.connection_info.authentication_info_model import AuthenticationInfo, BasicAuthAuthenticationInfo
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo
from mapa.gateway.constant import AuthenticationInfoTypes
from mapa.gateway.integration.integration_model import Integration, SpatialServiceType, SpatialConnection
from mapa.gateway.route.route_model import Route
from service.integration_handler.integration_handler import IntegrationHandler
from service.integration_handler.spatial.feature_handler import FeatureHandler
from service.integration_handler.spatial.tile_handler import TileHandler
from service.integration_handler.spatial.transaction_handler import TransactionHandler
from service.integration_handler.spatial.wms_handler import WmsHandler
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse
import json

def dummy_endpoint_func(request: FastapiResuest) -> FastapiResponse:
    """ApiRoute için kullanılacak dummy response handler fonksiyonu"""
    return FastapiResponse()

def auth_func(request: Request) -> Request:
    return request

class SpatialIntegrationHandler(IntegrationHandler):
    """Http İsteklerini karşılayan entegrasyon sınıfı"""

    def __init__(
        self,
        route: Route,
        path_params: Dict[str, Any]
    ) -> None:
        super().__init__(route, path_params)
        self._wms_handler = WmsHandler(self)
        self._tile_handler = TileHandler(self)
        self._feature_handler = FeatureHandler(self)
        self._transaction_handler = TransactionHandler(self)
        
    async def execute(self, service_request: ServiceRequest) -> ServiceResponse:
        if not self.integration.connection:
            raise ValueError("Connection not defined")

        # Backend bilgileri
        spatial_conn = SpatialConnection(**(self.integration.connection))
        match spatial_conn.service_type:
            case SpatialServiceType.WMS:
                return await self._wms_handler.execute(spatial_conn, service_request)
            case SpatialServiceType.Feature:
                return await self._feature_handler.execute(spatial_conn, service_request)
            case SpatialServiceType.Tile:
                return await self._tile_handler.execute(spatial_conn, service_request)
            case SpatialServiceType.Transaction:
                return await self._transaction_handler.execute(spatial_conn, service_request)
        raise ValueError('Spatial service type not found')