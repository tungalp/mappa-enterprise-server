
import uuid
from mapa.gateway.connection_info.connection_info_entity import ConnectionInfoEntity
from mapa.gateway.connection_info.authentication_info_model import AuthenticationInfo, BearerTokenAuthenticationInfo
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import HttpBackendConnection
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import ConnectionInfoTypes, IntegrationTypes, MethodTypes

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

product_api_name = str("dummy-api")
product_api_id = uuid.UUID("351fd5c0-0e9c-48ed-8809-704ab55226b7")
product_api = GatewayApiEntity(
    id = product_api_id,
    tenant_id = tenant_id,
    name = product_api_name,
    description = "product api description",
    path = "product",
    identifier = "http://gateway/test/product"
)

dummy_http_auth_connection_info_id = uuid.UUID("61d2209d-2995-4c6b-a7c0-4d5ab45b95e7")
dummy_http_auth_connection_info = ConnectionInfoEntity(
    id=dummy_http_auth_connection_info_id,
    tenant_id=tenant_id,
    name="Dummy Http Auth Bilgileri",
    type=ConnectionInfoTypes.AUTHENTICATION,
    params= AuthenticationInfo(
        auth_params = BearerTokenAuthenticationInfo(
            token="token"
        )
    ).model_dump()
)
# Get Products List
product_list_integration_id = uuid.UUID("33a677ab-9c81-4153-9d42-8ae0b7259960")
product_list_integration = IntegrationEntity(
    id = product_list_integration_id,
    tenant_id = tenant_id,
    name = "product list integration",
    description = "Product List Http Integration",
    context={},
    connection = HttpBackendConnection(
        method=MethodTypes.GET,
        endpoint="https://dummyjson.com/products"
    ).model_dump(),
    gateway_api_id = product_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.HTTP_BACKEND
)

product_list_route_id = uuid.UUID("49ea19a8-148e-4154-9d1b-172bce7935dd")
product_list_route = RouteEntity(
    id = product_list_route_id,
    tenant_id = tenant_id,
    description = "Product List Route",
    path = "list",
    scope = "openid",
    gateway_api_id = product_api_id,
    integration_id = product_list_integration_id
)

# GET Product By ID
product_get_integration_id = uuid.UUID("25010225-2773-4ab9-a94e-b10c090888b2")
product_get_integration = IntegrationEntity(
    id = product_get_integration_id,
    tenant_id = tenant_id,
    name = "product get integration",
    description = "Product Get HTTP Integration",
    context={},
    connection = HttpBackendConnection(
        method=MethodTypes.GET,
        endpoint="https://dummyjson.com/products/{product_id}"
    ).model_dump(),
    gateway_api_id = product_api_id,
    # connection_info_id=mock_http_auth_connection_info_id,
    type=IntegrationTypes.HTTP_BACKEND
)

product_get_route_id = uuid.UUID("866a6c11-8209-48b0-ae1b-1b8d31a91293")
product_get_route = RouteEntity(
    id = product_get_route_id,
    tenant_id = tenant_id,
    description = "Product Get Route",
    path = "item/{product_id}",
    scope = "read:product",
    gateway_api_id = product_api_id,
    integration_id = product_get_integration_id
)


instances = [
    product_api, dummy_http_auth_connection_info,
    product_list_integration, product_list_route,
    product_get_integration, product_get_route,
]
