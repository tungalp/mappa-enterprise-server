import random
from typing import List
from uuid import UUID, uuid4

from mapa.gateway.connection_info.authentication_info_model import (
    BasicAuthAuthenticationInfo, CreateAuthenticationInfo)
from mapa.gateway.constant import ApiTypes, AuthenticationInfoTypes, MethodTypes
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
from mapa.spatial.layer_definition.layer_definition_model import \
    CreateLayerDefinition
from mapa.spatial.layer_hook.layer_hook_model import CreateLayerHook
from mapa.spatial.map.map_model import CreateMap, Types
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
service_host = "http://localhost:33102"


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


def generate_namespace() -> CreateNamespace:
    return CreateNamespace(
        name="namespace_test_"+generate(size=4),
        title="Test"+generate(size=4),
        description="Test"+generate(size=4),
        identifier="https://namespace_identifier_"+generate(size=4))  # type: ignore


def generate_map(namespace_id: UUID = uuid4()) -> CreateMap:
    return CreateMap(
        name="map_test_"+generate(size=4),
        title="Test"+generate(size=4),
        description="Test"+generate(size=4),
        initial_extent="97.65656917606952;37.86541500399325;75.1803520939344;19.7160900653360" +
        str(random.randint(0, 10)),
        full_extent="46.333723794096386;46.29575588844355;23.85750671196024;30.02581711044706" +
        str(random.randint(0, 10)),
        srid=SridTypes.EPSG_3857,
        zoom=2,
        widget_types=[Types(key=MapWidgetType.AttributeTable), Types(
            key=MapWidgetType.Bookmark), Types(key=MapWidgetType.Info)]
    )  # type: ignore


def generate_connection(route_id: UUID = uuid4()) -> CreateConnection:
    return CreateConnection(
        route_params=[RouteParams(type=RouteParamsTypes.Wms, route_id=str(route_id)),
                      RouteParams(type=RouteParamsTypes.Feature, route_id=str(route_id))],
        description="Test"+generate(size=4),
        name="connection_test_"+generate(size=4),
        type= ConnectionTypes.External
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
                       opacity=round(random.uniform(0.0, 1.0), 1),
                       timer=False,
                       visible=True,
                       connection_id=connection_id,
                       field_params=[generate_field_params()],
                       geometry_field_param=generate_geometry_field_param(),
                       style_params=dict([]),
                       data_type=DataType.Png,
                       key_field="id",
                       type_name='test:title'
                       )


def generate_definition() -> CreateDefinition:
    return CreateDefinition(
        title="Test_layer_title"+generate(size=4),
        default_extent="",
        max_scale=random.randint(100, 10000),
        min_scale=random.randint(100, 10000),
        opacity=round(random.uniform(0.0, 1.0), 1),
        timer=False,
        is_attribute_panel=True,
        organization_geo_constraint=False,
        is_base_layer=True,
        field_params=[generate_field_params()],
        style_params=dict([]),
        topology_rules_params=[generate_topology_rules_params()],
        edit_snap_scale=random.randint(100, 10000),
        data_type=DataType.Png,
        filter_params=[generate_filter_params()],
        key_field="id",
        type_name='test:title'
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


def generate_authorization_info() -> CreateAuthenticationInfo:
    return CreateAuthenticationInfo(
        type=AuthenticationInfoTypes.BASICAUTH,
        auth_params=BasicAuthAuthenticationInfo(username="gomap", password="gomap.123"))


def generate_layer_definition(layer_id: UUID, definition_id: UUID) -> CreateLayerDefinition:
    return CreateLayerDefinition(layer_id=layer_id, definition_id=definition_id)


def generate_reference() -> List[CreateReference]:
    return [

        CreateReference(name="EPSG:3857", epsgcode="EPSG:3857", wkid="3857", wkt=str('PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]'),   projcs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"),
        CreateReference(name="EPSG:4230", epsgcode="EPSG:4230", wkid="4230", wkt=str(
            'GEOGCS["ED50",DATUM["European_Datum_1950",SPHEROID["International 1924",6378388,297,AUTHORITY["EPSG","7022"]],TOWGS84[-87,-98,-121,0,0,0,0],AUTHORITY["EPSG","6230"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4230"]]'),   projcs="+proj=longlat +ellps=intl +towgs84=-87,-98,-121,0,0,0,0 +no_defs"),
        CreateReference(name="EPSG:4326", epsgcode="EPSG:4326", wkid="4326", wkt=str(
            'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'),   projcs="+proj=longlat +datum=WGS84 +no_defs"),
        CreateReference(name="EPSG:5253", epsgcode="EPSG:5253", wkid="5253", wkt=str('PROJCS["TUREF / TM27",GEOGCS["TUREF",DATUM["Turkish_National_Reference_Frame",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1057"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","5252"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",27],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","5253"]]'),   projcs="+proj=tmerc +lat_0=0 +lon_0=27 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"),
        CreateReference(name="EPSG:5254", epsgcode="EPSG:5254", wkid="5254", wkt=str('PROJCS["TUREF / TM30",GEOGCS["TUREF",DATUM["Turkish_National_Reference_Frame",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1057"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","5252"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",30],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","5254"]]'),   projcs="+proj=tmerc +lat_0=0 +lon_0=30 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"),
        CreateReference(name="EPSG:5255", epsgcode="EPSG:5255", wkid="5255", wkt=str('PROJCS["TUREF / TM33",GEOGCS["TUREF",DATUM["Turkish_National_Reference_Frame",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1057"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","5252"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",33],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","5255"]]'),   projcs="+proj=tmerc +lat_0=0 +lon_0=33 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"),
        CreateReference(name="EPSG:5256", epsgcode="EPSG:5256", wkid="5256", wkt=str('PROJCS["TUREF / TM36",GEOGCS["TUREF",DATUM["Turkish_National_Reference_Frame",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1057"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","5252"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",36],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","5256"]]'),   projcs="+proj=tmerc +lat_0=0 +lon_0=36 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"),
        CreateReference(name="EPSG:5257", epsgcode="EPSG:5257", wkid="5257", wkt=str('PROJCS["TUREF / TM39",GEOGCS["TUREF",DATUM["Turkish_National_Reference_Frame",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1057"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","5252"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","5257"]]'),   projcs="+proj=tmerc +lat_0=0 +lon_0=39 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"),
        CreateReference(name="EPSG:5258", epsgcode="EPSG:5258", wkid="5258", wkt=str('PROJCS["TUREF / TM42",GEOGCS["TUREF",DATUM["Turkish_National_Reference_Frame",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1057"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","5252"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",42],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","5258"]]'),   projcs="+proj=tmerc +lat_0=0 +lon_0=42 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"),
        CreateReference(name="EPSG:5259", epsgcode="EPSG:5259", wkid="5259", wkt=str('PROJCS["TUREF / TM45",GEOGCS["TUREF",DATUM["Turkish_National_Reference_Frame",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","1057"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","5252"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",45],PARAMETER["scale_factor",1],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","5259"]]'),   projcs="+proj=tmerc +lat_0=0 +lon_0=45 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"),
        CreateReference(name="EPSG:32662", epsgcode="EPSG:32662", wkid="32662", wkt=str('PROJCS["WGS 84 / Plate Carree (deprecated)",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Equirectangular"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],AUTHORITY["EPSG","32662"]]'),   projcs="+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"),
        CreateReference(name="ESRI:54001", epsgcode="ESRI:54001", wkid="54001", wkt=str(
            'PROJCS["World_Plate_Carree",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]],PROJECTION["Equirectangular"],PARAMETER["standard_parallel_1",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["ESRI","54001"]]'),   projcs="+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"),
        CreateReference(name="ESRI:104122", epsgcode="ESRI:104122", wkid="104122", wkt=str(
            'GEOGCS["GCS_ITRF_1996",DATUM["International_Terrestrial_Reference_Frame_1996",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6654"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["ESRI","104122"]]'),   projcs="+proj=longlat +ellps=GRS80 +no_defs")
    ]


def generate_bookmark(user_id: UUID, map_id: UUID) -> CreateBookmark:
    return CreateBookmark(user_id=user_id,
                          map_id=map_id,
                          name="Test_name_book"+generate(size=4),
                          location=str(random.uniform(3624500.449655232, 3634500.449655232)) + ";" + str(
                              random.uniform(4858253.604920756, 4868253.604920756)) + ";" + str(3857) + ";" + str(random.randint(1, 20)),
                          thumbnail="Test_thumbnail_book"+generate(size=4))


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


def generate_field_params_list() -> List[FieldParams]:
    return [FieldParams(
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
    ),
        FieldParams(
        name="TEST",
        type="string",
        alias="",
        attribute_panel=True,
        listable=False,
        editable=True,
        multiple_editable=False,
        searchable=False,
        info=False,
        required=True,
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
    ]


def generate_geometry_field_param() -> GeometryFieldParam:
    return GeometryFieldParam(
        field_name="SHAPE",
        srid=SridTypes.EPSG_3857,
        type=GeometryType.Point
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

feature_collection = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
         "properties": {"prop0": "value0"}
         },
        {"type": "Feature",
         "geometry": {
             "type": "LineString",
             "coordinates": [
                 [102.0, 0.0], [103.0, 1.0], [
                     104.0, 0.0], [105.0, 1.0]
             ]
         },
         "properties": {
             "prop0": "value0",
             "prop1": 0.0
         }
         },
        {"type": "Feature",
         "geometry": {
             "type": "Polygon",
             "coordinates": [
                 [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                  [100.0, 1.0], [100.0, 0.0]]
             ]

         },
         "properties": {
             "prop0": "value0",
             "prop1": {"this": "that"}
         }
         }
    ]
}

features = [
    {"type": "Feature",
     "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
     "properties": {"prop0": "value0"}
     },
    {"type": "Feature",
     "geometry": {
             "type": "LineString",
             "coordinates": [
                 [102.0, 0.0], [103.0, 1.0], [
                     104.0, 0.0], [105.0, 1.0]
             ]
     },
     "properties": {
         "prop0": "value0",
         "prop1": 0.0
     }
     },
    {"type": "Feature",
     "geometry": {
             "type": "Polygon",
             "coordinates": [
                 [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                  [100.0, 1.0], [100.0, 0.0]]
             ]

     },
     "properties": {
         "prop0": "value0",
         "prop1": {"this": "that"}
     }
     }
]

feature = {"type": "Feature",
           "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
           "properties": {"prop0": "value0"}
           }

geo_data = {"name": "test", "geometry": {
    "type": "Point", "coordinates": [102.0, 0.5]}}

geo_datas = [{"name": "test1", "geometry": {
    "type": "Point", "coordinates": [100.0, 0.5]}},
    {"name": "test2", "geometry": {
        "type": "Point", "coordinates": [102.0, 0.5]}}]
