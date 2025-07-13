
import uuid
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import AdHocQueryConnection
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import IntegrationTypes, MethodTypes

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

lookup_api_id = uuid.UUID("1db515b5-8b93-4bda-9b3a-24b3b0db85ef")
lookup_api = GatewayApiEntity(
    id=lookup_api_id,
    tenant_id=tenant_id,
    name="lookup-api",
    description="Kisi Crud Lookup API",
    path="lookup",
    identifier="http://gateway/test/crud/lookup",
)

postgres_database_connection_info_id = uuid.UUID(
    "ce111d47-f3d9-492c-8920-8b4de8e8fed2")

# Lookup adres integration
lookup_adres_integration_id = uuid.UUID("c8b52382-0234-402f-afa0-98624209a305")
lookup_adres_integration = IntegrationEntity(
    id=lookup_adres_integration_id,
    tenant_id=tenant_id,
    name="Adres lookup integration",
    description="Adres lookup integration",
    context={},
    connection=AdHocQueryConnection(
        sql="select id, kapi_no from adhoc.adres",
        max_count=100,
        parent_column="parent_id"
    ).model_dump(),
    gateway_api_id=lookup_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

# Lookup adres
lookup_adres_route_id = uuid.UUID("04219fa1-9366-4953-b173-de332627ba49")
lookup_adres_route = RouteEntity(
    id=lookup_adres_route_id,
    tenant_id=tenant_id,
    description="Adres lookup route",
    method_type=MethodTypes.GET,
    path="adres",
    scope="openid",
    gateway_api_id=lookup_api_id,
    integration_id=lookup_adres_integration_id
)


# Lookup ulke integration
lookup_ulke_integration_id = uuid.UUID("774ef6aa-cf59-4a5a-9542-2fc4be9bd011")
lookup_ulke_integration = IntegrationEntity(
    id=lookup_ulke_integration_id,
    tenant_id=tenant_id,
    name="Ulke lookup integration",
    description="Adres ulke integration",
    context={},
    connection=AdHocQueryConnection(
        sql="select id, ad from adhoc.ulke",
        max_count=100,
        parent_column="parent_id"
    ).model_dump(),
    gateway_api_id=lookup_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

# Lookup ulke
lookup_ulke_route_id = uuid.UUID("536e57b8-8e58-479c-ab94-82226ba78820")
lookup_ulke_route = RouteEntity(
    id=lookup_ulke_route_id,
    tenant_id=tenant_id,
    description="Ulke lookup route",
    method_type=MethodTypes.GET,
    path="ulke",
    scope="openid",
    gateway_api_id=lookup_api_id,
    integration_id=lookup_ulke_integration_id
)

# Lookup il integration
lookup_il_integration_id = uuid.UUID("8490547c-e5b1-4656-b952-929ccd7841fa")
lookup_il_integration = IntegrationEntity(
    id=lookup_il_integration_id,
    tenant_id=tenant_id,
    name="İl lookup integration",
    description="Adres il integration",
    context={},
    connection=AdHocQueryConnection(
        sql="select id, ad from adhoc.il where ulke_id = :ulke_id",
        max_count=100
    ).model_dump(),
    gateway_api_id=lookup_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

# Lookup il
lookup_il_route_id = uuid.UUID("961f3101-bbbb-43bb-a16e-a09fc26ef409")
lookup_il_route = RouteEntity(
    id=lookup_il_route_id,
    tenant_id=tenant_id,
    description="il lookup route",
    method_type=MethodTypes.GET,
    path="il",
    query="ulke_id=:ulke_id",
    scope="openid",
    gateway_api_id=lookup_api_id,
    integration_id=lookup_il_integration_id
)

# Lookup ilce integration
lookup_ilce_integration_id = uuid.UUID("b6b098d5-eb8f-4a13-a1bf-877c311b075b")
lookup_ilce_integration = IntegrationEntity(
    id=lookup_ilce_integration_id,
    tenant_id=tenant_id,
    name="İlce lookup integration",
    description="Adres ilce integration",
    context={},
    connection=AdHocQueryConnection(
        sql="select id, ad from adhoc.ilce where il_id = :il_id",
        max_count=100
    ).model_dump(),
    gateway_api_id=lookup_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

# Lookup ilce
lookup_ilce_route_id = uuid.UUID("91a134a1-4456-4423-85d7-f3623e47438d")
lookup_ilce_route = RouteEntity(
    id=lookup_ilce_route_id,
    tenant_id=tenant_id,
    description="icel lookup route",
    method_type=MethodTypes.GET,
    path="ilce",
    query="il_id=:il_id",
    scope="openid",
    gateway_api_id=lookup_api_id,
    integration_id=lookup_ilce_integration_id
)

instances = [
    lookup_api,
    lookup_adres_integration, lookup_adres_route,
    lookup_ulke_integration, lookup_ulke_route,
    lookup_il_integration, lookup_il_route,
    lookup_ilce_integration, lookup_ilce_route,
]
