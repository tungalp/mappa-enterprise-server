
import json
import uuid
from mapa.gateway.connection_info.connection_info_entity import ConnectionInfoEntity
from mapa.gateway.connection_info.authentication_info_model import AuthenticationInfo, BearerTokenAuthenticationInfo
from mapa.gateway.connection_info.database_info_model import DatabaseInfo
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import HttpBackendConnection, SpatialBackendType, SpatialConnection, SpatialExternalBackend, SpatialServerType, SpatialServiceType, WmsServiceFormat
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import ConnectionInfoTypes, IntegrationTypes, MethodTypes, SqlResultTypes

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

spatial_api_name = str("spatial-api")
spatial_api_id = uuid.UUID("965f3be5-1330-4851-ab91-36b6ef339b70")
spatial_api = GatewayApiEntity(
    id = spatial_api_id,
    tenant_id = tenant_id,
    name = spatial_api_name,
    description = "spatial api description",
    path = "spatial",
    identifier = "http://gateway/test/spatial"
)

pg_conn_info_id = uuid.UUID("4aeb6d25-e85d-4610-9ded-7838cc5a457c")
pg_conn_info = ConnectionInfoEntity(
    id=pg_conn_info_id,
    tenant_id=tenant_id,
    name="Localhost Postgres Veritabanı Bağlantısı",
    type=ConnectionInfoTypes.DATABASE,
    params=DatabaseInfo(
        dialect="postgresql",
        database="mapa_test",
        username="mapa",
        host="db",
        port=5432,
        password="12345Abc."
    ).model_dump()
)

# WMS Integration
wms_integration_id = uuid.UUID("a1d56368-d3bd-4f5a-a7aa-e04db5e73000")
wms_integration = IntegrationEntity(
    id = wms_integration_id,
    tenant_id = tenant_id,
    name = "WMS Integration",
    description = "WMS Integration",
    connection = SpatialConnection(
        service_type=SpatialServiceType.WMS,
        backend=SpatialExternalBackend(
            type=SpatialBackendType.External,
            service_format=WmsServiceFormat.WMS_1_3_0,
            server_type=SpatialServerType.Geoserver,
            method=MethodTypes.GET,
            endpoint="http://host.docker.internal:8600/geoserver/ne/wms"
        )
    ).model_dump(),
    gateway_api_id = spatial_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.SPATIAL_BACKEND
)

wms_route_id = uuid.UUID("015eb5a4-9ea3-4bfb-83d6-ba1a2f4722a6")
wms_route = RouteEntity(
    id = wms_route_id,
    tenant_id = tenant_id,
    description = "WMS Route",
    path = "wms",
    scope = "",
    gateway_api_id = spatial_api_id,
    integration_id = wms_integration_id
)

instances = [
    spatial_api, pg_conn_info,
    wms_integration, wms_route
]