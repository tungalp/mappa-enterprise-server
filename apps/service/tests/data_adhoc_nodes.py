
import uuid
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import AdHocQueryConnection
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import IntegrationTypes, MethodTypes

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

nodes_api_id = uuid.UUID("5083729a-c790-413f-a088-b0e1cde3054b")
nodes_api = GatewayApiEntity(
    id=nodes_api_id,
    tenant_id=tenant_id,
    name="nodes-api",
    description="nodes hierarchical description",
    path="nodes",
    identifier="http://gateway/test/nodes",
    context={
        "empty": {}
    }
)

postgres_database_connection_info_id = uuid.UUID(
    "ce111d47-f3d9-492c-8920-8b4de8e8fed2")

# Nodes CRUD integration
nodes_integration_id = uuid.UUID("09c6ec84-fefc-4f00-b3cd-a728b77a6535")
nodes_integration = IntegrationEntity(
    id=nodes_integration_id,
    tenant_id=tenant_id,
    name="nodes hierarchical table integration",
    description="nodes hierarchical table integration",
    context={},
    connection=AdHocQueryConnection(
        sql="public.nodes",
        max_count=100,
        parent_column="parent_id"
    ).model_dump(),
    gateway_api_id=nodes_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

# Nodes paging
nodes_get_route_id = uuid.UUID("0521be1e-1941-462d-9ac4-b5819a6a27d5")
nodes_get_route = RouteEntity(
    id=nodes_get_route_id,
    tenant_id=tenant_id,
    description="Nodes Paging Route",
    method_type=MethodTypes.GET,
    path="",
    scope="openid",
    gateway_api_id=nodes_api_id,
    integration_id=nodes_integration_id
)

instances = [
    nodes_api,
    nodes_integration,
    nodes_get_route
]
