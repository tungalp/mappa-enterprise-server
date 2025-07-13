
import uuid
from mapa.gateway.context_var.context_var_entity import ContextVarEntity
from mapa.gateway.connection_info.authentication_info_model import BasicAuthAuthenticationInfo, CreateAuthenticationInfo
from mapa.gateway.connection_info.connection_info_model import CreateConnectionInfo
from mapa.gateway.connection_info.database_info_model import CreateDatabaseInfo
from mapa.gateway.context_var.context_var_model import CreateConvextVar
from mapa.gateway.parameter_mapping.parameter_mapping_model import CreateParameterMapping, CreateRequestResponseMapping
from mapa.test.base_app_fixture import BaseAppFixture
from gateway.app import create_application
from nanoid import generate
from uuid import UUID, uuid4
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi, GatewayApi
from mapa.gateway.route.route_model import CreateRoute, Route
from mapa.gateway.integration.integration_model import CreateIntegration, FeatureServiceFormat, HttpBackendConnection, Integration, SpatialBackendType, SpatialConnection, SpatialExternalBackend, SpatialServerType, SpatialServiceType, WmsServiceFormat
from mapa.gateway.constant import ApiTypes, ConnectionInfoTypes, ParameterMappingTypes, MethodTypes, IntegrationTypes, AuthenticationInfoTypes, ModifierTypes, ParameterTypes, ValueTypes, ModifierTypes, ParameterTypes, ValueTypes

tenant_id = "10a2238f-4d1e-4626-9f3c-799d3ef5e96d"

var_1_id = uuid.UUID("239ffe3e-8bd8-4561-b5f6-c7349a59d6ab")
var_1 = ContextVarEntity(
    id=var_1_id,
    key="X-IBM-CLIENT_ID",
    value="Client-ID-Company-1",
    tenant_id=uuid.UUID(tenant_id)
)

var_2_id = uuid.UUID("1a34b468-3be0-4ebe-a147-60dc1f233c38")
var_2 = ContextVarEntity(
    id=var_2_id,
    key="X-IBM-CLIENT_SECRET",
    value="BMhDH0peagDYc3tqCfuog",
    tenant_id=uuid.UUID(tenant_id)
)

var_3_id = uuid.UUID("26757e4e-59ea-4a9c-bea1-a9b6c3e7e7c3")
var_3 = ContextVarEntity(
    id=var_3_id,
    key="company_name",
    value="google inc",
    tenant_id=uuid.UUID(tenant_id)
)

instances = [
    var_1, var_2, var_3
]

api_scopes = ["query:api", "edit:api", "query:api_scope", "edit:api_scope", "query:client", "edit:client", "query:client_api", "edit:client_api", "query:client_api_scope", "edit:client_api_scope", "query:invitation", "edit:invitation", "query:profile_adaptor", "edit:profile_adaptor", "query:role", "edit:role", "query:role_api_scope", "edit:role_api_scope", "query:role_user", "edit:role_user", "query:user", "edit:user", "query:application", "edit:application", "query:content_page", "edit:content_page", "query:content_page_template", "edit:content_page_template", "query:connection_info", "edit:connection_info", "query:context_var", "edit:context_var",
              "query:gateway_api", "edit:gateway_api", "query:integration", "edit:integration", "query:parameter_mapping", "edit:parameter_mapping", "query:route", "edit:route", "query:base_layer", "edit:base_layer", "query:bookmark", "edit:bookmark", "query:connection", "edit:connection", "query:definition", "edit:definition", "query:hook", "edit:hook", "query:layer", "edit:layer", "query:layer_definition", "edit:layer_definition", "query:layer_hook", "edit:layer_hook", "query:map", "edit:map", "query:map_base_layer", "edit:map_base_layer", "query:map_layer", "edit:map_layer", "query:namespace", "edit:namespace", "query:reference", "edit:reference"]



def generate_gateway_api() -> CreateGatewayApi:
    return CreateGatewayApi(description="Test desc"+generate(size=4),
                            name="Test api"+generate(size=4),
                            type=ApiTypes.HTTP,
                            path="Test api path"+generate(size=4),
                            identifier="Test identifier"+generate(size=4),
                            context={
                                "client_id": "client_id_test",
                                "client_secret": "client_secret_test"
    })


def generate_integration(gateway_api_id: UUID = uuid4(), connection_info_id: UUID = uuid4()) -> CreateIntegration:
    return CreateIntegration(description="Test integration desc"+generate(size=4),
                             name="Test integration"+generate(size=4),
                             type=IntegrationTypes.HTTP_BACKEND,
                             gateway_api_id=gateway_api_id,
                             connection_info_id=connection_info_id,
                             context={},
                             connection=HttpBackendConnection(method="GET", endpoint="p1").model_dump(),default_route=False,default_route_path="")


def generate_route(gateway_api_id: UUID = uuid4()) -> CreateRoute:
    return CreateRoute(description="Test route desc"+generate(size=4),
                       path="/Test path/"+generate(size=4),
                       method_type=MethodTypes.GET,
                       gateway_api_id=gateway_api_id)


def generate_authorization_info() -> CreateAuthenticationInfo:
    return CreateAuthenticationInfo(
        type=AuthenticationInfoTypes.BASICAUTH,
        auth_params=BasicAuthAuthenticationInfo(username="u1", password="p1"))


def generate_database_info() -> CreateDatabaseInfo:
    return CreateDatabaseInfo(
        dialect="oracle",
        username="scott",
        password="tiger",
        host="127.0.0.1",
        port=8800,
        database="sidname",)


def generate_request_parameter_mapping(status_code: int, integration_id: UUID = uuid4()) -> CreateParameterMapping:
    return CreateParameterMapping(
        status_code=status_code,
        type=ParameterMappingTypes.REQUEST,
        param_list=[
            CreateRequestResponseMapping(
                parameter_type=ParameterTypes.HEADER,
                parameter="token",
                modifier=ModifierTypes.APPEND,
                value_type=ValueTypes.HEADER,
                value="id").model_dump(),

            CreateRequestResponseMapping(
                parameter_type=ParameterTypes.BODY,
                parameter=ParameterTypes.BODY,
                modifier=ModifierTypes.OVERWRITE,
                value_type=ValueTypes.STATIC,
                value="4400").model_dump()
        ],
        integration_id=integration_id,)


def generate_response_parameter_mapping(status_code: int, integration_id: UUID = uuid4()) -> CreateParameterMapping:
    return CreateParameterMapping(
        status_code=status_code,
        type=ParameterMappingTypes.RESPONSE,
        param_list=[
            CreateRequestResponseMapping(
                parameter_type=ParameterTypes.HEADER,
                parameter="token",
                modifier=ModifierTypes.APPEND,
                value_type=ValueTypes.HEADER,
                value="id").model_dump(),

            CreateRequestResponseMapping(
                parameter_type=ParameterTypes.BODY,
                parameter=ParameterTypes.BODY,
                modifier=ModifierTypes.OVERWRITE,
                value_type=ValueTypes.STATIC,
                value="4400").model_dump()
        ],
        integration_id=integration_id,)


def generate_context_var() -> CreateConvextVar:
    return CreateConvextVar(
        key=f"key_{generate(size=4)}",
        value=f"value_{generate(size=4)}"
    )


def generate_connection_info() -> CreateConnectionInfo:
    return CreateConnectionInfo(
        name=f"name{generate(size=4)}",
        description=f"description{generate(size=4)}",
        type=ConnectionInfoTypes.AUTHENTICATION,
        params=generate_authorization_info().model_dump()
    )


# Not spatial tarafındaki gomap örnek dataları için hazırlanmış
generate_gateway_api_gomap_id = uuid.UUID("9395253e-2b59-4a77-9ac8-2b66d0559371")
def generate_gateway_api_gomap() -> GatewayApi:
    return GatewayApi(id=generate_gateway_api_gomap_id,
        description="gomap_test"+generate(size=4),
                            name="gomap_test"+generate(size=4),
                            type=ApiTypes.HTTP,
                            path="gomap",
                            identifier="https://gomap"+generate(size=4),
                            context={
                                "client_id": "client_id_test",
                                "client_secret": "client_secret_test"
    }) 
    
def generate_authorization_info_gomap() -> CreateAuthenticationInfo:
    return CreateAuthenticationInfo(
        type=AuthenticationInfoTypes.BASICAUTH,
        auth_params=BasicAuthAuthenticationInfo(username="gomap", password="gomap.123"))
    
    
#  WMS için integration  
generate_integration_wms_gomap_id = uuid.UUID("17af5996-fb88-4621-b01b-38a155b3db61")
def generate_integration_external_wms_gomap(gateway_api_id: UUID = uuid4(), connection_info_id: UUID = uuid4()) -> Integration:
    return Integration(id = generate_integration_wms_gomap_id,
                             description="Test integration desc"+generate(size=4),
                             name="Test integration"+generate(size=4),
                             type=IntegrationTypes.SPATIAL_BACKEND,
                             gateway_api_id=gateway_api_id,
                             connection_info_id=connection_info_id,
                             context={},
                             connection=SpatialConnection(service_type=SpatialServiceType.WMS, backend=generate_integration_external_backend_wms_gomap()).model_dump(),default_route=False,default_route_path="")


def generate_integration_external_backend_wms_gomap()->SpatialExternalBackend:
    return SpatialExternalBackend(type=SpatialBackendType.External,
                                  server_type=SpatialServerType.Geoserver,
                                  service_format=WmsServiceFormat.WMS_1_3_0,
                                  method=MethodTypes.GET,
                                  endpoint="https://cbsservis.kgm.gov.tr/geoserver/btm/ows")
    

#  Feature için integration   
generate_integration_feature_gomap_id = uuid.UUID("17af5996-fb88-4621-b01b-38a155b3db62")
def generate_integration_external_feature_gomap(gateway_api_id: UUID = uuid4(), connection_info_id: UUID = uuid4()) -> Integration:
    return Integration(id = generate_integration_feature_gomap_id,
                             description="Test integration desc"+generate(size=4),
                             name="Test integration"+generate(size=4),
                             type=IntegrationTypes.SPATIAL_BACKEND,
                             gateway_api_id=gateway_api_id,
                             connection_info_id=connection_info_id,
                             context={},
                             connection=SpatialConnection(service_type=SpatialServiceType.Feature, backend=generate_integration_external_backend_feature_gomap()).model_dump(),default_route=False,default_route_path="")


def generate_integration_external_backend_feature_gomap()->SpatialExternalBackend:
    return SpatialExternalBackend(type=SpatialBackendType.External,
                                  server_type=SpatialServerType.Geoserver,
                                  service_format=FeatureServiceFormat.WFS_2_0_0,
                                  method=MethodTypes.GET,
                                  endpoint="https://cbsservis.kgm.gov.tr/geoserver/btm/ows")    
    

generate_integration_gomap_id = uuid.UUID("b3c1993f-8aa9-4094-abb8-b5ce1afc5431")
def generate_route_gomap_wms(gateway_api_id: UUID = uuid4(),integration_id: UUID= uuid4()) -> Route:
    return Route(id=generate_integration_gomap_id,
                       description="wms route",
                       path="wms",
                       method_type=MethodTypes.GET,
                       gateway_api_id=gateway_api_id,
                       integration_id=integration_id)
    
    
generate_route_gomap_feature_get_id = uuid.UUID("b3c1993f-8aa9-4094-abb8-b5ce1afc5431")
def generate_route_gomap_feature_get(gateway_api_id: UUID = uuid4(),integration_id: UUID= uuid4()) -> Route:
    return Route(id=generate_route_gomap_feature_get_id,
                       description="wfs get route",
                       path="wfs",
                       method_type=MethodTypes.GET,
                       gateway_api_id=gateway_api_id,
                       integration_id=integration_id)
    
    
generate_route_gomap_feature_post_id = uuid.UUID("2d10dc09-c0ff-4cc5-b84b-48325cdabdd1")
def generate_route_gomap_feature_post(gateway_api_id: UUID = uuid4(),integration_id: UUID= uuid4()) -> Route:
    return Route(id=generate_route_gomap_feature_post_id,
                       description="wfs post route",
                       path="wfs",
                       method_type=MethodTypes.POST,
                       gateway_api_id=gateway_api_id,
                       integration_id=integration_id)



route_field_list = [  
                            "id",
                            "description",
                            "method_type",
                            "path",
                            "query",
                            "gateway_api_id",
                            "integration_id",
                            "scope",
                            "integration.id",
                            "integration.name",
                            "integration.timeout_in_millis",
                            "integration.type",
                            "integration.connection",
                            "integration.gateway_api_id",
                            "integration.context",
                            "gateway_api.id",
                            "gateway_api.name",
                            "gateway_api.type",
                            "gateway_api.path",
                            "gateway_api.identifier"
                          ]

integration_select_list = [  
                            "id",
                            "name",
                            "description",
                            "timeout_in_millis",
                            "context",
                            "type",
                            "connection",
                            "connection_info_id",
                            "gateway_api_id",
                            "gateway_api.id",
                            "gateway_api.name",
                            "gateway_api.type",
                            "gateway_api.path",
                            "gateway_api.identifier",
                            "connection_info.id",
                            "connection_info.name",
                            "connection_info.description",
                            "connection_info.type",
                            "connection_info.params",
                          ]