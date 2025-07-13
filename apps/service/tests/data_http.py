
import json
import uuid
from mapa.gateway.connection_info.connection_info_entity import ConnectionInfoEntity
from mapa.gateway.connection_info.authentication_info_model import AuthenticationInfo, BearerTokenAuthenticationInfo
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import HttpBackendConnection
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import ConnectionInfoTypes, IntegrationTypes, MethodTypes, SqlResultTypes

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

parsel_api_name = str("parsel-api")
parsel_api_id = uuid.UUID("569d6503-74d6-4fbc-8352-678d47074436")
parsel_api = GatewayApiEntity(
    id = parsel_api_id,
    tenant_id = tenant_id,
    name = parsel_api_name,
    description = "parsel api description",
    path = "parsel",
    identifier = "http://gateway/test/parsel"
)

mock_http_auth_connection_info_id = uuid.UUID("ac16d7ae-a467-4688-be90-bff0bd3079e9")
mock_http_auth_connection_info = ConnectionInfoEntity(
    id=mock_http_auth_connection_info_id,
    tenant_id=tenant_id,
    name="Mock Http Auth Bilgileri",
    type=ConnectionInfoTypes.AUTHENTICATION,
    params= AuthenticationInfo(
        auth_params = BearerTokenAuthenticationInfo(
            token="token"
        )
    ).model_dump()
)
# Get Parsel List
parsel_list_integration_id = uuid.UUID("0d9b7607-004f-4185-a062-5ae9b6fdc1da")
parsel_list_integration = IntegrationEntity(
    id = parsel_list_integration_id,
    tenant_id = tenant_id,
    name = "parsel list integration",
    description = "Parsel List Http Integration",
    context={},
    connection = HttpBackendConnection(
        method=MethodTypes.GET,
        endpoint="http://localhost:33200/parsel/list"
    ).model_dump(),
    gateway_api_id = parsel_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.HTTP_BACKEND
)

parsel_list_route_id = uuid.UUID("f4f01e7b-f557-4011-bb07-6b48bf80bb87")
parsel_list_route = RouteEntity(
    id = parsel_list_route_id,
    tenant_id = tenant_id,
    description = "Parsel List Route",
    path = "",
    scope = "openid",
    gateway_api_id = parsel_api_id,
    integration_id = parsel_list_integration_id
)

# GET Parsel By ID
parsel_get_integration_id = uuid.UUID("d933dee2-edf4-498f-aaff-82e7e07f4023")
parsel_get_integration = IntegrationEntity(
    id = parsel_get_integration_id,
    tenant_id = tenant_id,
    name = "parsel get integration",
    description = "Parsel Get HTTP Integration",
    context={},
    connection = HttpBackendConnection(
        method=MethodTypes.GET,
        endpoint="http://localhost:33200/parsel/{parsel_id}"
    ).model_dump(),
    gateway_api_id = parsel_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.HTTP_BACKEND
)

parsel_get_route_id = uuid.UUID("f6b3b30d-9f3a-4118-87b1-9dae8f052873")
parsel_get_route = RouteEntity(
    id = parsel_get_route_id,
    tenant_id = tenant_id,
    description = "Parsel Get Route",
    path = "{parsel_id:int}",
    scope = "read:parsel",
    gateway_api_id = parsel_api_id,
    integration_id = parsel_get_integration_id
)

# POST Create Kisi
parsel_post_integration_id = uuid.UUID("2923d8e3-6c4e-4a25-a7e2-6e75298c9a16")
parsel_post_integration = IntegrationEntity(
    id = parsel_post_integration_id,
    tenant_id = tenant_id,
    name = "parsel post integration",
    description = "Parsel POST HTTP Integration",
    context={},
    connection = HttpBackendConnection(
        method=MethodTypes.POST,
        endpoint="http://localhost:33200/parsel/"
    ).model_dump(),
    gateway_api_id = parsel_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.HTTP_BACKEND
)

parsel_post_route_id = uuid.UUID("e614ec1d-da28-410a-9130-9175f430a5cf")
parsel_post_route = RouteEntity(
    id = parsel_post_route_id,
    tenant_id = tenant_id,
    description = "Kisi POST Route",
    method_type = MethodTypes.POST,
    path = "",
    scope = "create:parsel",
    gateway_api_id = parsel_api_id,
    integration_id = parsel_post_integration_id
)

# PUT Update Parsel
parsel_put_integration_id = uuid.UUID("786eaa2a-4376-4aa5-b8e4-11c29d5012f2")
parsel_put_integration = IntegrationEntity(
    id = parsel_put_integration_id,
    tenant_id = tenant_id,
    name = "parsel put integration",
    description = "Parsel PUT HTTP Integration",
    context={},
    connection = HttpBackendConnection(
        method=MethodTypes.PUT,
        endpoint="http://localhost:33200/parsel/{parsel_id}"
    ).model_dump(),
    gateway_api_id = parsel_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.HTTP_BACKEND
)

parsel_put_route_id = uuid.UUID("25cc2f82-7fe5-437c-b391-027d396127fe")
parsel_put_route = RouteEntity(
    id = parsel_put_route_id,
    tenant_id = tenant_id,
    description = "Parsel POST Route",
    method_type = MethodTypes.PUT,
    path = "{parsel_id:int}",
    scope = "update:parsel",
    gateway_api_id = parsel_api_id,
    integration_id = parsel_put_integration_id
)

# DELETE Delete Parsel
parsel_delete_integration_id = uuid.UUID("0620fb38-ac8e-4e90-a0d7-f7f7d6dfa3c9")
parsel_delete_integration = IntegrationEntity(
    id = parsel_delete_integration_id,
    tenant_id = tenant_id,
    name = "parsel delete integration",
    description = "Parsel DELETE HTTP Integration",
    context={},
    connection = HttpBackendConnection(
        method=MethodTypes.DELETE,
        endpoint="http://localhost:33200/parsel/{parsel_id}"
    ).model_dump(),
    gateway_api_id = parsel_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.HTTP_BACKEND    
)

parsel_delete_route_id = uuid.UUID("f8f42211-24fd-4013-90d7-b7521f484534")
parsel_delete_route = RouteEntity(
    id = parsel_delete_route_id,
    tenant_id = tenant_id,
    description = "Parsel DELETE Route",
    method_type = MethodTypes.DELETE,
    path = "{parsel_id:int}",
    scope = "delete:parsel",
    gateway_api_id = parsel_api_id,
    integration_id = parsel_delete_integration_id
)

# Any
any_integration_id = uuid.UUID("fb8394d7-5e4c-4ebb-bdd2-73973b1e6b07")
any_integration = IntegrationEntity(
    id = any_integration_id,
    tenant_id = tenant_id,
    name = "Parsel Any integration",
    description = "Parsel Any HTTP Integration",
    context={},
    connection = HttpBackendConnection(
        method=MethodTypes.ANY,
        endpoint="http://localhost:33200/any/"
    ).model_dump(),
    gateway_api_id = parsel_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.HTTP_BACKEND    
)

any_route_id = uuid.UUID("a6f20920-37a0-4995-872f-d67db47ddeff")
any_route = RouteEntity(
    id = any_route_id,
    tenant_id = tenant_id,
    description = "Parsel ANY Route",
    method_type = MethodTypes.ANY,
    path = "any",
    scope = "",
    gateway_api_id = parsel_api_id,
    integration_id = any_integration_id
)

instances = [
    parsel_api, mock_http_auth_connection_info,
    parsel_list_integration, parsel_list_route,
    parsel_get_integration, parsel_get_route,
    parsel_post_integration, parsel_post_route,
    parsel_put_integration, parsel_put_route,
    parsel_delete_integration, parsel_delete_route,
    any_integration, any_route
]
