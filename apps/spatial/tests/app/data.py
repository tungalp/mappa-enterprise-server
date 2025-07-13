import random
from typing import Any, List
from uuid import UUID, uuid4

from mapa.gateway.constant import ApiTypes, MethodTypes
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi
from mapa.gateway.route.route_model import CreateRoute
from mapa.spatial.base_layer.base_layer_model import (BaseLayerConnection,
                                                     CreateBaseLayer)
from mapa.spatial.bookmark.bookmark_model import CreateBookmark
from mapa.spatial.connection.connection_model import (CreateConnection,
                                                     RouteParams)
from mapa.spatial.constant import (BaseLayerTypes, ConnectionTypes, DataType, GeometryType,
                                  HookOperationType, HookType, MapServiceTypes,
                                  MapWidgetType, OperatorType,
                                  RouteParamsTypes, RuleType, SridTypes)
from mapa.spatial.definition.definition_model import CreateDefinition
from mapa.spatial.hook.hook_model import CreateHook
from mapa.spatial.layer.layer_model import CreateLayer
from mapa.spatial.layer_hook.layer_hook_model import CreateLayerHook
from mapa.spatial.map.map_model import CreateMap
from mapa.spatial.map_base_layer.map_base_layer_model import CreateMapBaseLayer
from mapa.spatial.map_layer.map_layer_model import CreateMapLayer, Params
from mapa.spatial.models.field_params_model import FieldParams
from mapa.spatial.models.filter_params_model import FilterParams
from mapa.spatial.models.geometry_field_param_model import GeometryFieldParam
from mapa.spatial.models.topology_rules_params_model import TopologyRulesParams
from mapa.spatial.namespace.namespace_model import CreateNamespace
from mapa.spatial.reference.reference_model import CreateReference
from nanoid import generate


tenant_id = "10a2238f-4d1e-4626-9f3c-799d3ef5e96d"

def generate_hook_list() -> List[CreateHook]:
    return [CreateHook(
        type=HookType.Layer,
        operation_type=HookOperationType.DELETE,
        description="Test"+generate(size=4)
    ),
        CreateHook(
        type=HookType.Layer,
        operation_type=HookOperationType.GET,
        description="Test"+generate(size=4)
    ),
        CreateHook(
        type=HookType.Layer,
        operation_type=HookOperationType.POST,
        description="Test"+generate(size=4)
    ),
        CreateHook(
        type=HookType.Layer,
        operation_type=HookOperationType.PUT,
        description="Test"+generate(size=4)
    )]


def generate_layer_hook(route_id: UUID = uuid4(), layer_definition_id: UUID = uuid4(),
                        hook_operation_type: HookOperationType = HookOperationType.GET) -> CreateLayerHook:
    return CreateLayerHook(
        route_id=route_id,
        layer_definition_id=layer_definition_id,
        widget_name=MapWidgetType.Editor,
        hook_operation_type=hook_operation_type
    )


def generate_map_base_layer(map_id: UUID = uuid4(), base_layer_id: UUID = uuid4()) -> CreateMapBaseLayer:
    return CreateMapBaseLayer(
        order=random.randint(1, 100),
        base_layer_id=base_layer_id,
        map_id=map_id)  # type: ignore


def generate_base_layer() -> CreateBaseLayer:
    return CreateBaseLayer(
        type=BaseLayerTypes.WebMapService,
        connection=BaseLayerConnection(name='test__', thumbnail="base64", tiles=['https://mt0.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                 'https://mt1.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                 'https://mt2.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                 'https://mt3.google.com/vt/lyrs=y&z={z}&x={x}&y={y}'], tile_size=256))



def generate_bookmark(user_id: Any, map_id: UUID) -> CreateBookmark:
    return CreateBookmark(user_id=user_id,
                          map_id=map_id,
                          name="Test_name_book"+generate(size=4),
                          location=str(random.uniform(3624500.449655232, 3634500.449655232)) + ";" + str(
                              random.uniform(4858253.604920756, 4868253.604920756)) + ";" + str(3857),
                          thumbnail="Test_thumbnail_book"+generate(size=4))


def generate_namespace() -> CreateNamespace:
    return CreateNamespace(
        name="namespace_test_"+generate(size=4),
        title="Test"+generate(size=4),
        description="Test"+generate(size=4),
        identifier="https://namespace_identifier_"+generate(size=4))  # type: ignore


def generate_map(namespace_id: UUID = uuid4()) -> CreateMap:
    return CreateMap(
        namespace_id=namespace_id,
        name="map_test_"+generate(size=4),
        title="Test"+generate(size=4),
        description="Test"+generate(size=4),
        initial_extent="97.65656917606952;37.86541500399325;75.1803520939344;19.7160900653360" +
        str(random.randint(0, 10)),
        full_extent="46.333723794096386;46.29575588844355;23.85750671196024;30.02581711044706" +
        str(random.randint(0, 10)),
        srid=SridTypes.EPSG_3857,
        zoom=12
    )  # type: ignore


def generate_connection(route_id: UUID = uuid4()) -> CreateConnection:
    return CreateConnection(
        route_params=[RouteParams(type=RouteParamsTypes.Wms, route_id=str(route_id)),
                      RouteParams(type=RouteParamsTypes.Feature, route_id=str(route_id))],
        description="Test"+generate(size=4),
        name="connection_test_"+generate(size=4),
        type=ConnectionTypes.External
    )  # type: ignore


def generate_gateway_api() -> CreateGatewayApi:
    return CreateGatewayApi(description="Test desc"+generate(size=4),
                            name="Test api"+generate(size=4),
                            type=ApiTypes.HTTP,
                            path="Testapipath"+generate(size=4),
                            identifier="identfier"+generate(size=4),
                            context=dict({
                                "x-ibm-client-id": "client-id-test",
                                "x-ibm-client-secret": "client-secret",
                                "secret": {
                                    "username": "test",
                                    "password": "test-password",
                                    "loginCount": 123
                                }
                            }))


def generate_route(gateway_api_id: UUID = uuid4()) -> CreateRoute:
    return CreateRoute(description="Test route desc"+generate(size=4),
                       path="/Testpath/"+generate(size=4),
                       method_type=MethodTypes.GET,
                       query="?id={id}",
                       gateway_api_id=gateway_api_id)


def generate_layer(connection_id: UUID = uuid4()) -> CreateLayer:
    return CreateLayer(name="Test_layer"+generate(size=4),
                       description="Test_layer_desc"+generate(size=4),
                       title="Test_layer_title"+generate(size=4),
                       code="",
                       default_extent="",
                       max_scale=random.randint(100, 10000),
                       min_scale=random.randint(100, 10000),
                       opacity=random.randint(0, 1),
                       timer=False,
                       visible=True,
                       connection_id=connection_id,
                       field_params=[generate_field_params()],
                       geometry_field_param=generate_geometry_field_param(),
                       style_params=dict([]),
                       data_type=DataType.Png,
                       key_field="id",
                       type_name="test:layer",
                       )


def generate_definition() -> CreateDefinition:
    return CreateDefinition(
        title="Test_layer_title"+generate(size=4),
        default_extent="",
        max_scale=random.randint(100, 10000),
        min_scale=random.randint(100, 10000),
        opacity=random.randint(0, 1),
        timer=False,
        is_attribute_panel=True,
        organization_geo_constraint=False,
        is_base_layer=True,
        field_params=[generate_field_params()],
        style_params=dict([]),
        topology_rules_params=[generate_topology_rules_params()],
        edit_snap_scale=random.randint(100, 10000),
        data_type=DataType.Png,
        key_field="id",
        type_name="test:layer",
        filter_params=[generate_filter_params()],
    )


def generate_topology_rules_params() -> TopologyRulesParams:
    return TopologyRulesParams(
        name="test",
        destination_layer_id="1",
        rule_type=RuleType.Contains,
        tolerance=random.randint(1, 5),
    )


def generate_filter_params() -> FilterParams:
    return FilterParams(
        operator=OperatorType.ILIKE,
        key="AD",
        value="1"
    )


def generate_route_params(type=RouteParamsTypes.Wms, route_id: UUID = uuid4()) -> RouteParams:
    return RouteParams(
        type=RouteParamsTypes.Wms,
        route_id=str(route_id)
    )


def generate_map_layer(map_id: UUID = uuid4(), layer_definition_id: UUID = uuid4()) -> CreateMapLayer:
    return CreateMapLayer(
        name="Test_name"+generate(size=4),
        order=random.randint(0, 1),
        map_id=map_id,
        layer_definition_id=layer_definition_id,
        params=generate_params()
    )


def generate_params() -> Params:
    return Params(
        visible=True,
        opacity=random.randint(0, 1),
    )


def generate_reference() -> List[CreateReference]:
    return [
        CreateReference(name="EPSG:" + str(random.randint(3857, 4000)),epsgcode="EPSG:" + str(random.randint(3857, 4000)), wkid="3857", wkt=str('PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]'),   projcs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"),
        CreateReference(name="EPSG:" + str(random.randint(3857, 4000)),epsgcode="EPSG:" + str(random.randint(3857, 4000)), wkid="3857", wkt=str('PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]'),   projcs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"),
    ]


def generate_geometry_field_param() -> GeometryFieldParam:
    return GeometryFieldParam(
        field_name="SHAPE",
        srid=SridTypes.EPSG_3857,
        type=GeometryType.Point
    )


def generate_field_params() -> FieldParams:
    return FieldParams(
        name="RID",
        type="string",
        alias="",
        attribute_panel=False,
        listable=False,
        editable=False,
        multiple_editable=False,
        searchable=False,
        info=False,
        required=False,
        length=12,
        definitions=None,
        validation_rules=[],
        sortable=True,
        text_search=False,
        order=1,
        value_path="Admin/apipath/routepath",
        label_prop_name='ad',
        value_prop_name='id'
    )


map_info_select = [
    "id",
    "name",
    "description",
    "title",
    "initial_extent",
    "full_extent",
    "widget_types",
    "srid",
    "zoom",

    "namespace_id",
    "namespace.id",
    "namespace.name",
    "namespace.description",
    "namespace.title",
    "namespace.identifier",

    "map_layers.id",
    "map_layers.name",
    "map_layers.order",
    "map_layers.parent_id",
    "map_layers.params",
    "map_layers.map_id",
    "map_layers.layer_definition_id",

    "map_layers.layer_definition.id",
    "map_layers.layer_definition.layer_id",

    "map_layers.layer_definition.layer.id",
    "map_layers.layer_definition.layer.name",
    "map_layers.layer_definition.layer.code",
    "map_layers.layer_definition.layer.description",
    "map_layers.layer_definition.layer.title",
    "map_layers.layer_definition.layer.default_extent",
    "map_layers.layer_definition.layer.max_scale",
    "map_layers.layer_definition.layer.min_scale",
    "map_layers.layer_definition.layer.opacity",
    "map_layers.layer_definition.layer.timer",
    "map_layers.layer_definition.layer.visible",
    "map_layers.layer_definition.layer.field_params",
    "map_layers.layer_definition.layer.geometry_field_param",
    "map_layers.layer_definition.layer.style_params",
    "map_layers.layer_definition.layer.connection_id",
    "map_layers.layer_definition.layer.data_type",
    "map_layers.layer_definition.layer.key_field",
    "map_layers.layer_definition.layer.type_name",

    "map_layers.layer_definition.layer.connection.id",
    "map_layers.layer_definition.layer.connection.name",
    "map_layers.layer_definition.layer.connection.description",
    "map_layers.layer_definition.layer.connection.route_params",
    "map_layers.layer_definition.layer.connection.type",

    "map_layers.layer_definition.definition_id",
    "map_layers.layer_definition.definition.id",
    "map_layers.layer_definition.definition.title",
    "map_layers.layer_definition.definition.default_extent",
    "map_layers.layer_definition.definition.max_scale",
    "map_layers.layer_definition.definition.min_scale",
    "map_layers.layer_definition.definition.opacity",
    "map_layers.layer_definition.definition.timer",
    "map_layers.layer_definition.definition.is_attribute_panel",
    "map_layers.layer_definition.definition.organization_geo_constraint",
    "map_layers.layer_definition.definition.is_base_layer",
    "map_layers.layer_definition.definition.edit_snap_scale",
    "map_layers.layer_definition.definition.data_type",
    "map_layers.layer_definition.definition.key_field",
    "map_layers.layer_definition.definition.type_name",
    "map_layers.layer_definition.definition.field_params",
    "map_layers.layer_definition.definition.style_params",
    "map_layers.layer_definition.definition.topology_rules_params",
    "map_layers.layer_definition.definition.filter_params",

    "map_layers.layer_definition.layer_hooks.id",
    "map_layers.layer_definition.layer_hooks.route_id",
    "map_layers.layer_definition.layer_hooks.layer_definition_id",
    "map_layers.layer_definition.layer_hooks.widget_name",
    "map_layers.layer_definition.layer_hooks.hook_operation_type",
]


map_base_layer_select = [
    "id",
    "order",
    "map_id",
    "base_layer_id",
    "base_layer.id",
    "base_layer.type",
    "base_layer.connection",
]

api_scopes = ["query:api", "edit:api", "query:api_scope", "edit:api_scope", "query:client", "edit:client", "query:client_api", "edit:client_api", "query:client_api_scope", "edit:client_api_scope", "query:invitation", "edit:invitation", "query:profile_adaptor", "edit:profile_adaptor", "query:role", "edit:role", "query:role_api_scope", "edit:role_api_scope", "query:role_user", "edit:role_user", "query:user", "edit:user", "query:application", "edit:application", "query:content_page", "edit:content_page", "query:content_page_template", "edit:content_page_template", "query:connection_info", "edit:connection_info", "query:context_var", "edit:context_var",
              "query:gateway_api", "edit:gateway_api", "query:integration", "edit:integration", "query:parameter_mapping", "edit:parameter_mapping", "query:route", "edit:route", "query:base_layer", "edit:base_layer", "query:bookmark", "edit:bookmark", "query:connection", "edit:connection", "query:definition", "edit:definition", "query:hook", "edit:hook", "query:layer", "edit:layer", "query:layer_definition", "edit:layer_definition", "query:layer_hook", "edit:layer_hook", "query:map", "edit:map", "query:map_base_layer", "edit:map_base_layer", "query:map_layer", "edit:map_layer", "query:namespace", "edit:namespace", "query:reference", "edit:reference"]

