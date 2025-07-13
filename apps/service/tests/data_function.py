
import uuid
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import IntegrationTypes, MethodTypes

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

function_api_id = uuid.UUID("3b86d7a6-6aac-4904-b3d1-d9b8d0dce1bf")
function_api = GatewayApiEntity(
    id=function_api_id,
    tenant_id=tenant_id,
    name="function-api",
    description="function",
    path="function",
    identifier="http://gateway/test/function",
    context={
        "empty": {}
    }
)

# Function integration
function_integration_id = uuid.UUID("5f32e9a3-6e01-48bb-bbb6-bb6312b8dcde")
function_integration = IntegrationEntity(
    id=function_integration_id,
    tenant_id=tenant_id,
    name="function integration",
    description="function integration",
    context={},
    connection={
        "runtime_id": "123",
        "handler": "test:handler"
    },
    gateway_api_id=function_api_id,
    type=IntegrationTypes.FUNCTIONS
)

# Function route
function_get_route_id = uuid.UUID("fc6e1639-eabe-41bd-85bf-01897bceb90a")
function_get_route = RouteEntity(
    id=function_get_route_id,
    tenant_id=tenant_id,
    description="Function Route",
    method_type=MethodTypes.ANY,
    path="test/handler",
    scope="openid",
    gateway_api_id=function_api_id,
    integration_id=function_integration_id
)

# Function integration 2
function_integration_id_2 = uuid.UUID("10eec640-6d37-4549-b783-49280616306d")
function_integration_2 = IntegrationEntity(
    id=function_integration_id_2,
    tenant_id=tenant_id,
    name="function integration 2",
    description="function integration 2",
    context={},
    connection={
        "runtime_id": "456",
        "handler": "test:handler2"
    },
    gateway_api_id=function_api_id,
    type=IntegrationTypes.FUNCTIONS
)

# Function route 2
function_get_route_id_2 = uuid.UUID("e90b44c8-4cda-4043-a92b-359041d9aca7")
function_get_route_2 = RouteEntity(
    id=function_get_route_id_2,
    tenant_id=tenant_id,
    description="Function Route",
    method_type=MethodTypes.ANY,
    path="test/handler2",
    scope="openid",
    gateway_api_id=function_api_id,
    integration_id=function_integration_id_2
)

# Function integration 3
function_integration_id_3 = uuid.UUID("635c7636-9da7-414e-86b7-4870a6590438")
function_integration_3 = IntegrationEntity(
    id=function_integration_id_3,
    tenant_id=tenant_id,
    name="function integration 3",
    description="function integration 3",
    context={},
    connection={
        "runtime_id": "789",
        "handler": "test:handler3"
    },
    gateway_api_id=function_api_id,
    type=IntegrationTypes.FUNCTIONS
)

# Function route 3
function_get_route_id_3 = uuid.UUID("194d2092-b4ca-4f8e-87d0-4f4baf348dbb")
function_get_route_3 = RouteEntity(
    id=function_get_route_id_3,
    tenant_id=tenant_id,
    description="Function Route",
    method_type=MethodTypes.ANY,
    path="test/handler3",
    scope="openid",
    gateway_api_id=function_api_id,
    integration_id=function_integration_id_3
)

instances = [
    function_api,
    function_integration, function_get_route,
    function_integration_2, function_get_route_2,
    function_integration_3, function_get_route_3,
]
