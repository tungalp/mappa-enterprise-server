
import uuid
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import AdHocQueryConnection
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import IntegrationTypes, MethodTypes

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

kisi_api_id = uuid.UUID("0a0addd8-ea18-4392-939e-f83290a692be")

postgres_database_connection_info_id = uuid.UUID(
    "ce111d47-f3d9-492c-8920-8b4de8e8fed2")

# Kisi CRUD integration
kisi_crud_integration_id = uuid.UUID("db7be480-1c2f-4203-bcb2-7e832b9253b6")
kisi_crud_integration = IntegrationEntity(
    id=kisi_crud_integration_id,
    tenant_id=tenant_id,
    name="kisi crud  paging integration",
    description="Kisi Crud Paging DB Integration",
    context={},
    connection=AdHocQueryConnection(
        sql="adhoc.kisi",
        max_count=100,
        parent_column="parent_id"
    ).model_dump(),
    gateway_api_id=kisi_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

# Kisi paging
kisi_crud_get_route_id = uuid.UUID("9a99da1e-7994-4355-93b2-b8307f3c4d0b")
kisi_crud_get_route = RouteEntity(
    id=kisi_crud_get_route_id,
    tenant_id=tenant_id,
    description="Kisi Crud Paging Route",
    method_type=MethodTypes.GET,
    path="crud",
    # scope="openid",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_crud_integration_id
)

kisi_crud_post_route_id = uuid.UUID("62600a7d-2a39-4dba-a44d-6e1cdcb37263")
kisi_crud_post_route = RouteEntity(
    id=kisi_crud_post_route_id,
    tenant_id=tenant_id,
    description="Kisi Crud POST Route",
    method_type=MethodTypes.POST,
    path="crud",
    # scope="create:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_crud_integration_id
)

kisi_crud_put_route_id = uuid.UUID("2b25c513-5584-448d-902a-5c309fa78020")
kisi_crud_put_route = RouteEntity(
    id=kisi_crud_put_route_id,
    tenant_id=tenant_id,
    description="Kisi Crud POST Route",
    method_type=MethodTypes.PUT,
    path="crud",
    # scope="update:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_crud_integration_id
)

kisi_crud_delete_route_id = uuid.UUID("ca62e043-99f1-4d31-8fc2-fb84239abf50")
kisi_crud_delete_route = RouteEntity(
    id=kisi_crud_delete_route_id,
    tenant_id=tenant_id,
    description="Kisi DELETE Route",
    method_type=MethodTypes.DELETE,
    path="crud",
    # scope="delete:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_crud_integration_id
)

# Kisi2 CRUD integration
kisi2_crud_integration_id = uuid.UUID("78a5071d-4bea-48da-804f-561eb11836a1")
kisi2_crud_integration = IntegrationEntity(
    id=kisi2_crud_integration_id,
    tenant_id=tenant_id,
    name="kisi2 crud  paging integration",
    description="Kisi Crud Paging DB Integration",
    context={},
    connection=AdHocQueryConnection(
        sql="adhoc.kisi2",
        max_count=100
    ).model_dump(),
    gateway_api_id=kisi_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

# Kisi2 paging
kisi2_crud_get_route_id = uuid.UUID("96fc75c2-dda8-4079-aebd-edec2dd7b666")
kisi2_crud_get_route = RouteEntity(
    id=kisi2_crud_get_route_id,
    tenant_id=tenant_id,
    description="Kisi2 Crud Paging Route",
    method_type=MethodTypes.GET,
    path="crud2",
    # scope="openid",
    gateway_api_id=kisi_api_id,
    integration_id=kisi2_crud_integration_id
)

kisi2_crud_post_route_id = uuid.UUID("21744e1b-ca89-431c-aa8a-ba6513a77fb9")
kisi2_crud_post_route = RouteEntity(
    id=kisi2_crud_post_route_id,
    tenant_id=tenant_id,
    description="Kisi Crud POST Route",
    method_type=MethodTypes.POST,
    path="crud2",
    # scope="create:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi2_crud_integration_id
)

kisi2_crud_put_route_id = uuid.UUID("6a574bda-6cbd-4656-8df9-78cd892c9383")
kisi2_crud_put_route = RouteEntity(
    id=kisi2_crud_put_route_id,
    tenant_id=tenant_id,
    description="Kisi2 Crud POST Route",
    method_type=MethodTypes.PUT,
    path="crud2",
    # scope="update:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi2_crud_integration_id
)

kisi2_crud_delete_route_id = uuid.UUID("968392d1-d9af-4c94-ab3b-dec56863e3dd")
kisi2_crud_delete_route = RouteEntity(
    id=kisi2_crud_delete_route_id,
    tenant_id=tenant_id,
    description="Kisi DELETE Route",
    method_type=MethodTypes.DELETE,
    path="crud2",
    # scope="delete:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi2_crud_integration_id
)
instances = [
    kisi_crud_integration,
    kisi_crud_get_route,
    kisi_crud_post_route,
    kisi_crud_put_route,
    kisi_crud_delete_route,
    kisi2_crud_integration,
    kisi2_crud_get_route,
    kisi2_crud_post_route,
    kisi2_crud_put_route,
    kisi2_crud_delete_route    
]
