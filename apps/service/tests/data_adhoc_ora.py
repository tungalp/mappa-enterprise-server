import uuid
from mapa.gateway.connection_info.connection_info_entity import ConnectionInfoEntity
from mapa.gateway.connection_info.database_info_model import DatabaseInfo
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import AdHocQueryConnection
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import ConnectionInfoTypes, IntegrationTypes

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

idari_api_name = str("idari-api")
idari_api_id = uuid.UUID("dc41d059-a20d-4911-84e4-c1055b7e7215")
idari_api = GatewayApiEntity(
    id = idari_api_id,
    tenant_id = tenant_id,
    name = idari_api_name,
    description = "idari api description",
    path = "idari",
    identifier = "http://gateway/test/idari"
)

oracle_database_connection_info_id = uuid.UUID("572c77b2-fdf7-45a7-a2b0-ee450e7772dd")
oracle_database_connection_info = ConnectionInfoEntity(
    id=oracle_database_connection_info_id,
    tenant_id=tenant_id,
    name="Ofis Oracle Veritabanı Bağlantısı",
    type=ConnectionInfoTypes.DATABASE,
    params= DatabaseInfo(
        dialect="oracle",
        database="DEV",
        username="INSTALLER",
        host="10.6.2.102",
        port=1521,
        password="ISLEM22"
    ).model_dump()
)
# Get Il List
il_list_integration_id = uuid.UUID("e4c608c9-6185-4f07-9831-0d9268770d62")
il_list_integration = IntegrationEntity(
    id = il_list_integration_id,
    tenant_id = tenant_id,
    name = "il list integration",
    description = "Il List DB Integration",
    context={},
    connection = AdHocQueryConnection(
        sql="select ID, CD, KIMLIKNO, AD from IDR_100.IDR_IL",
        max_count=2
    ).model_dump(),
    gateway_api_id = idari_api_id,
    connection_info_id=oracle_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

il_list_route_id = uuid.UUID("1866bf91-99fa-47ba-9a8d-1d1521bd5330")
il_list_route = RouteEntity(
    id = il_list_route_id,
    tenant_id = tenant_id,
    description = "Il List Route",
    path = "il",
    scope = "openid",
    gateway_api_id = idari_api_id,
    integration_id = il_list_integration_id
)

instances = [
    idari_api, oracle_database_connection_info,
    il_list_integration, il_list_route
]
