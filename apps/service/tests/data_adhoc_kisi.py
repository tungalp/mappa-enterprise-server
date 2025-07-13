import json
import uuid
from mapa.gateway.connection_info.connection_info_entity import ConnectionInfoEntity
from mapa.gateway.connection_info.database_info_model import DatabaseInfo
from mapa.gateway.context_var.context_var_entity import ContextVarEntity
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import AdHocQueryConnection
from mapa.gateway.parameter_mapping.parameter_mapping_entity import ParameterMappingEntity
from mapa.gateway.parameter_mapping.parameter_mapping_model import RequestResponseMapping
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import ConnectionInfoTypes, IntegrationTypes, MethodTypes, ParameterMappingTypes, SqlResultTypes, ParameterTypes, ModifierTypes, ValueTypes

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

context_var_id = uuid.UUID("2669aea7-31d4-44b8-a7f2-172cd63470f0")
context_var = ContextVarEntity(
    id=context_var_id,
    key="company",
    value={
        "name": "test-company",
        "owner": "test owner"
    },
    tenant_id=tenant_id
)

context_var_2_id = uuid.UUID("7b456204-9293-4b4d-82b1-4704e53d911f")
context_var_2 = ContextVarEntity(
    id=context_var_2_id,
    key="test",
    value={
        "test_var": "test_var",
        "test_var_2": "test_var-2"
    },
    tenant_id=tenant_id
)

kisi_api_name = str("kisi-api")
kisi_api_id = uuid.UUID("0a0addd8-ea18-4392-939e-f83290a692be")
kisi_api = GatewayApiEntity(
    id=kisi_api_id,
    tenant_id=tenant_id,
    name=kisi_api_name,
    description="kisi api description",
    path="kisi",
    identifier="http://gateway/test/kisi",
    context={
        "client_id": "kisi_client_id",
        "client_secret": "kisi_client_secret",
        "empty": {}
    }
)

postgres_database_connection_info_id = uuid.UUID(
    "ce111d47-f3d9-492c-8920-8b4de8e8fed2")
postgres_database_connection_info = ConnectionInfoEntity(
    id=postgres_database_connection_info_id,
    tenant_id=tenant_id,
    name="Localhost Postgres Veritabanı Bağlantısı",
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
# Get Kisi List
kisi_list_integration_id = uuid.UUID("f9425170-2ccf-4826-9240-c3a39d8eb93d")
kisi_list_integration = IntegrationEntity(
    id=kisi_list_integration_id,
    tenant_id=tenant_id,
    name="kisi list integration",
    description="Kisi List DB Integration",
    context={},
    connection=AdHocQueryConnection(
        sql="select * from adhoc.kisi where ad ilike :ad and soyad ilike :soyad",
        max_count=2
    ).model_dump(),
    gateway_api_id=kisi_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

kisi_list_route_id = uuid.UUID("9bac19bb-e43e-4238-a48e-af22bcb64ca4")
kisi_list_route = RouteEntity(
    id=kisi_list_route_id,
    tenant_id=tenant_id,
    description="Kisi List Route",
    path="",
    scope="openid",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_list_integration_id
)

# Get Kisi List With Parameter Mapping
kisi_list_2_integration_id = uuid.UUID("b7aa4d81-5231-4d0e-89b8-ca67a9c72526")
kisi_list_2_integration = IntegrationEntity(
    id=kisi_list_2_integration_id,
    tenant_id=tenant_id,
    name="kisi list 2 integration",
    description="Kisi List 2 DB Integration",
    context={},
    connection=AdHocQueryConnection(
        sql="select * from adhoc.kisi where ad ilike :ad and soyad ilike :soyad",
        max_count=2
    ).model_dump(),
    gateway_api_id=kisi_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

param_mapping_id = uuid.UUID("1334bfa6-e826-4314-a24b-d7928b60f7fe")
param_mapping = ParameterMappingEntity(
    id=param_mapping_id,
    status_code=0,
    type=ParameterMappingTypes.REQUEST,
    integration_id=kisi_list_2_integration_id,
    param_list=[
        RequestResponseMapping(
            parameter_type=ParameterTypes.HEADER,
            parameter="X-Test-Header",
            modifier=ModifierTypes.OVERWRITE,
            value_type=ValueTypes.STATIC,
            value="Modified Test Header"
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.QUERY,
            parameter="ad",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.QUERY,
            value="name"
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.QUERY,
            parameter="soyad",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.STATIC,
            value="%2%"
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.HEADER,
            parameter="X-Will-Remove-Header",
            modifier=ModifierTypes.REMOVE,
            value_type="",
            value=""
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.QUERY,
            parameter="name",
            modifier=ModifierTypes.REMOVE,
            value_type="",
            value=""
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.QUERY,
            parameter="surname",
            modifier=ModifierTypes.REMOVE,
            value_type="",
            value=""
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.BODY,
            parameter="company",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.CONTEXT,
            value="company"
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.BODY,
            parameter="company_name",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.CONTEXT,
            value="company.name"
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.BODY,
            parameter="company.test",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.CONTEXT,
            value="test.test_var"
        ).model_dump()
    ]
)


param_mapping_2_id = uuid.UUID("b9663f83-6659-4fef-ab37-8e39db8a9dd2")
param_mapping_2 = ParameterMappingEntity(
    id=param_mapping_2_id,
    status_code=200,
    type=ParameterMappingTypes.RESPONSE,
    integration_id=kisi_list_2_integration_id,
    param_list=[
        RequestResponseMapping(
            parameter_type=ParameterTypes.HEADER,
            parameter="Y-Test-Header",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.STATIC,
            value="RESPONSE Test Header"
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.BODY,
            parameter="append_test",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.STATIC,
            value="eklenen_değer"
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.BODY,
            parameter="affected",
            modifier=ModifierTypes.OVERWRITE,
            value_type=ValueTypes.STATIC,
            value="11111"
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.BODY,
            parameter="user_id",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.CONTEXT,
            value="user_id"
        ).model_dump(),
        RequestResponseMapping(
            parameter_type=ParameterTypes.BODY,
            parameter="company",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.CONTEXT,
            value="empty"
        ).model_dump(),     
        RequestResponseMapping(
            parameter_type=ParameterTypes.BODY,
            parameter="company.test",
            modifier=ModifierTypes.APPEND,
            value_type=ValueTypes.CONTEXT,
            value="test.test_var_2"
        ).model_dump()
    ]
)

kisi_list_2_route_id = uuid.UUID("cd8e8585-7ce5-4d0f-a2d8-f539aee21000")
kisi_list_2_route = RouteEntity(
    id=kisi_list_2_route_id,
    tenant_id=tenant_id,
    description="Kisi List 2 Route",
    path="list",
    scope="openid",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_list_2_integration_id
)

# GET Kisi By ID
kisi_get_integration_id = uuid.UUID("31335115-4458-4d3c-b696-ac8e4d1056a0")
kisi_get_integration = IntegrationEntity(
    id=kisi_get_integration_id,
    tenant_id=tenant_id,
    name="kisi get integration",
    description="Kisi Get HTTP Integration",
    context={},
    connection=AdHocQueryConnection(
        sql="select * from adhoc.kisi where id = :kisi_id",
        result_type=SqlResultTypes.SINGLE
    ).model_dump(),
    gateway_api_id=kisi_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

kisi_get_route_id = uuid.UUID("546fea7e-bc73-4af4-bebf-25ea3afa9f05")
kisi_get_route = RouteEntity(
    id=kisi_get_route_id,
    tenant_id=tenant_id,
    description="Kisi Get Route",
    path="{kisi_id:int}",
    scope="read:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_get_integration_id
)


# POST Create Kisi
kisi_post_integration_id = uuid.UUID("0da56302-fd98-4c98-a20d-ce9b99091773")
kisi_post_integration = IntegrationEntity(
    id=kisi_post_integration_id,
    tenant_id=tenant_id,
    name="kisi post integration",
    description="Kisi POST HTTP Integration",
    context={},
    connection=AdHocQueryConnection(
        sql="insert into adhoc.kisi (ad, soyad, ev_adres_id, is_adres_id, ilce_id) "
            "values (:ad, :soyad, :ev_adres_id, :is_adres_id, :ilce_id) "
            "returning id, ad, soyad, ev_adres_id, is_adres_id, ilce_id",
    ).model_dump(),
    gateway_api_id=kisi_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

kisi_post_route_id = uuid.UUID("d38f6185-7884-4ab6-a74b-fc2563f0e983")
kisi_post_route = RouteEntity(
    id=kisi_post_route_id,
    tenant_id=tenant_id,
    description="Kisi POST Route",
    method_type=MethodTypes.POST,
    path="",
    scope="create:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_post_integration_id
)

# PUT Update Kisi
kisi_put_integration_id = uuid.UUID("9712a1a1-db26-4cc4-817a-49bb96b78dcf")
kisi_put_integration = IntegrationEntity(
    id=kisi_put_integration_id,
    tenant_id=tenant_id,
    name="kisi put integration",
    description="Kisi PUT HTTP Integration",
    context={},
    connection=AdHocQueryConnection(
        sql="update adhoc.kisi set ad = :ad, soyad = :soyad where id = :kisi_id returning id, ad, soyad, ev_adres_id, is_adres_id, ilce_id",
        result_type=SqlResultTypes.MULTI
    ).model_dump(),
    gateway_api_id=kisi_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

kisi_put_route_id = uuid.UUID("cfa62954-6e83-4869-b5eb-5a2f88c312ef")
kisi_put_route = RouteEntity(
    id=kisi_put_route_id,
    tenant_id=tenant_id,
    description="Kisi POST Route",
    method_type=MethodTypes.PUT,
    path="{kisi_id:int}",
    scope="update:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_put_integration_id
)

# DELETE Delete Kisi
kisi_delete_integration_id = uuid.UUID("4945f3fb-cf16-48d9-82ef-58288ef383c0")
kisi_delete_integration = IntegrationEntity(
    id=kisi_delete_integration_id,
    tenant_id=tenant_id,
    name="kisi delete integration",
    description="Kisi DELETE HTTP Integration",
    context={},
    connection=AdHocQueryConnection(
        sql="delete from adhoc.kisi where id = :kisi_id returning id, ad, soyad, ev_adres_id, is_adres_id, ilce_id",
        result_type=SqlResultTypes.MULTI
    ).model_dump(),
    gateway_api_id=kisi_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)

kisi_delete_route_id = uuid.UUID("7b268fa2-d6f8-409b-ad33-250659f822fb")
kisi_delete_route = RouteEntity(
    id=kisi_delete_route_id,
    tenant_id=tenant_id,
    description="Kisi DELETE Route",
    method_type=MethodTypes.DELETE,
    path="{kisi_id:int}",
    scope="delete:kisi",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_delete_integration_id
)

# Get All Kisi List
kisi_all_list_integration_id = uuid.UUID("b4a9f438-0fa9-4bfe-97c4-d74ebbf4ee54")
kisi_all_list_integration = IntegrationEntity(
    id=kisi_all_list_integration_id,
    tenant_id=tenant_id,
    name="kisi all list integration",
    description="Kisi All List DB Integration",
    context={},
    connection=AdHocQueryConnection(
        sql="select * from adhoc.kisi",
        max_count=100
    ).model_dump(),
    gateway_api_id=kisi_api_id,
    connection_info_id=postgres_database_connection_info_id,
    type=IntegrationTypes.ADHOC_QUERY
)
kisi_all_list_route_id = uuid.UUID("db9852c9-f898-48dc-b777-7df2016f4496")
kisi_all_list_route = RouteEntity(
    id=kisi_all_list_route_id,
    tenant_id=tenant_id,
    description="Kisi List Route",
    path="all",
    query="?query={query}",
    scope="openid",
    gateway_api_id=kisi_api_id,
    integration_id=kisi_all_list_integration_id
)

instances = [
    context_var, context_var_2,
    kisi_api, postgres_database_connection_info,
    kisi_list_integration, kisi_list_route,
    kisi_list_2_integration, kisi_list_2_route, param_mapping, param_mapping_2,
    kisi_get_integration, kisi_get_route,
    kisi_post_integration, kisi_post_route,
    kisi_put_integration, kisi_put_route,
    kisi_delete_integration, kisi_delete_route,
    kisi_all_list_integration, kisi_all_list_route
]
