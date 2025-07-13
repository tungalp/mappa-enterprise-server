
import json
import uuid
from mapa.gateway.connection_info.connection_info_entity import ConnectionInfoEntity
from mapa.gateway.connection_info.authentication_info_model import AuthenticationInfo, BearerTokenAuthenticationInfo
from mapa.gateway.connection_info.database_info_model import DatabaseInfo
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import FeatureServiceFormat, HttpBackendConnection, SpatialBackendType, SpatialConnection, SpatialExternalBackend, SpatialServerType, SpatialServiceType, TileServiceFormat, TransactionServiceFormat, WmsServiceFormat
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
    name="Localhost PG DB Conn",
    type=ConnectionInfoTypes.DATABASE,
    params=DatabaseInfo(
        dialect="postgresql",
        database="esp_test",
        username="esp",
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


# WFS Integration
wfs_integration_id = uuid.UUID("1d33498b-40a2-4ac3-b1d6-aca32a41ed9c")
wfs_integration = IntegrationEntity(
    id = wfs_integration_id,
    tenant_id = tenant_id,
    name = "Feature Integration",
    description = "Feature Integration",
    connection = SpatialConnection(
        service_type=SpatialServiceType.Feature,
        backend=SpatialExternalBackend(
            type=SpatialBackendType.External,
            service_format=FeatureServiceFormat.WFS_2_0_0,
            server_type=SpatialServerType.Geoserver,
            method=MethodTypes.GET,
            endpoint="http://host.docker.internal:8600/geoserver/ne/wfs"
        )
    ).model_dump(),
    gateway_api_id = spatial_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.SPATIAL_BACKEND
)

wfs_route_id = uuid.UUID("ce4417ba-d4b3-4809-9668-61d5b2b85fe2")
wfs_route = RouteEntity(
    id = wfs_route_id,
    tenant_id = tenant_id,
    description = "Feature Route",
    path = "wfs",
    scope = "",
    gateway_api_id = spatial_api_id,
    integration_id = wfs_integration_id
)

# Tile WMTS Integration
wmts_integration_id = uuid.UUID("e51ac543-0215-414b-aed4-63fdc394966c")
wmts_integration = IntegrationEntity(
    id = wmts_integration_id,
    tenant_id = tenant_id,
    name = "WMTS Integration",
    description = "WMTS Integration",
    connection = SpatialConnection(
        service_type=SpatialServiceType.Tile,
        backend=SpatialExternalBackend(
            type=SpatialBackendType.External,
            service_format=TileServiceFormat.WMTS,
            server_type=SpatialServerType.Geoserver,
            method=MethodTypes.GET,
            endpoint="http://host.docker.internal:8600/geoserver/ne/gwc/service/wmts"
        )
    ).model_dump(),
    gateway_api_id = spatial_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.SPATIAL_BACKEND
)

wmts_route_id = uuid.UUID("c7bbeaa5-d800-41e6-9829-b1f48ee25fb0")
wmts_route = RouteEntity(
    id = wmts_route_id,
    tenant_id = tenant_id,
    description = "WMTS Route",
    path = "tile/wmts/{typename}/{z}/{x}/{y}.{format}",
    scope = "",
    gateway_api_id = spatial_api_id,
    integration_id = wmts_integration_id
)

# Tile XYZ Integration
xyz_integration_id = uuid.UUID("c61993ea-bdd8-4f99-8cc5-d6c5ed71d627")
xyz_integration = IntegrationEntity(
    id = xyz_integration_id,
    tenant_id = tenant_id,
    name = "XYZ Integration",
    description = "XYZ Integration",
    connection = SpatialConnection(
        service_type=SpatialServiceType.Tile,
        backend=SpatialExternalBackend(
            type=SpatialBackendType.External,
            service_format=TileServiceFormat.XYZ,
            server_type=SpatialServerType.Geoserver,
            method=MethodTypes.GET,
            endpoint="https://a.tiles.azavea.com/nlcd/{z}/{x}/{y}.png"
        )
    ).model_dump(),
    gateway_api_id = spatial_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.SPATIAL_BACKEND
)

xyz_route_id = uuid.UUID("6a50afff-2892-4f4e-b0c7-774b96fbb645")
xyz_route = RouteEntity(
    id = xyz_route_id,
    tenant_id = tenant_id,
    description = "XYZ Route",
    path = "tile/xyz/nlcd/{z}/{x}/{y}.png",
    scope = "",
    gateway_api_id = spatial_api_id,
    integration_id = xyz_integration_id
)

# Tile XYZ Integration
xyz_2_integration_id = uuid.UUID("7939396e-6a81-467b-98b4-83097c00b21a")
xyz_2_integration = IntegrationEntity(
    id = xyz_2_integration_id,
    tenant_id = tenant_id,
    name = "XYZ 2 Integration",
    description = "XYZ 2 Integration",
    connection = SpatialConnection(
        service_type=SpatialServiceType.Tile,
        backend=SpatialExternalBackend(
            type=SpatialBackendType.External,
            service_format=TileServiceFormat.XYZ,
            server_type=SpatialServerType.Geoserver,
            method=MethodTypes.GET,
            endpoint="https://a.tiles.azavea.com/{typename}/{z}/{x}/{y}.{format}"
        )
    ).model_dump(),
    gateway_api_id = spatial_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.SPATIAL_BACKEND
)

xyz_2_route_id = uuid.UUID("cb40b3fd-4c7f-4a11-9b5e-7ef6e39cf534")
xyz_2_route = RouteEntity(
    id = xyz_2_route_id,
    tenant_id = tenant_id,
    description = "XYZ 2 Route",
    path = "tile/xyz_2/{typename}/{z}/{x}/{y}.{format}",
    scope = "",
    gateway_api_id = spatial_api_id,
    integration_id = xyz_2_integration_id
)

# Transaction Integration
transaction_integration_id = uuid.UUID("b29ab901-861b-417c-91e0-24a74831dc8a")
transaction_integration = IntegrationEntity(
    id = transaction_integration_id,
    tenant_id = tenant_id,
    name = "Transaction Integration",
    description = "Transaction Integration",
    connection = SpatialConnection(
        service_type=SpatialServiceType.Transaction,
        backend=SpatialExternalBackend(
            type=SpatialBackendType.External,
            service_format=TransactionServiceFormat.WFS_T_2_0_0,
            server_type=SpatialServerType.Geoserver,
            method=MethodTypes.ANY,
            endpoint="http://host.docker.internal:8600/geoserver/wfs"
        )
    ).model_dump(),
    gateway_api_id = spatial_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.SPATIAL_BACKEND
)

transaction_route_id = uuid.UUID("9f6d4b2e-b1fe-4cec-97a0-97afac7e85ef")
transaction_route = RouteEntity(
    id = transaction_route_id,
    tenant_id = tenant_id,
    description = "Transaction Route",
    path = "transaction",
    scope = "",
    gateway_api_id = spatial_api_id,
    integration_id = transaction_integration_id,
    method_type = MethodTypes.ANY
)


instances = [
    spatial_api, pg_conn_info,
    wms_integration, wms_route,
    wfs_integration, wfs_route,
    wmts_integration, wmts_route,
    xyz_integration, xyz_route,
    xyz_2_integration, xyz_2_route,
    transaction_integration, transaction_route
]