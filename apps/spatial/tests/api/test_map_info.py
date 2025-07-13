import asyncio
import random
from typing import Any, Dict, List
from uuid import uuid4

import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.connection_info.connection_info_model import \
    CreateConnectionInfo
from mapa.gateway.connection_info.connection_info_service import \
    ConnectionInfoService
from mapa.gateway.constant import (ApiTypes, ConnectionInfoTypes,
                                  IntegrationTypes, MethodTypes)
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService
from mapa.gateway.integration.integration_model import (CreateIntegration,
                                                       HttpBackendConnection)
from mapa.gateway.integration.integration_service import IntegrationService
from mapa.gateway.route.route_model import CreateRoute
from mapa.gateway.route.route_service import RouteService
from mapa.spatial.base_layer.base_layer_model import (BaseLayerConnection,
                                                     CreateBaseLayer)
from mapa.spatial.base_layer.base_layer_service import BaseLayerService
from mapa.spatial.bookmark.bookmark_model import CreateBookmark
from mapa.spatial.bookmark.bookmark_service import BookmarkService
from mapa.spatial.connection.connection_model import (CreateConnection,
                                                     RouteParams)
from mapa.spatial.connection.connection_service import ConnectionService
from mapa.spatial.constant import (BaseLayerTypes, ConnectionTypes, DataType, HookOperationType,
                                  MapServiceTypes, MapWidgetType,
                                  RouteParamsTypes, SridTypes)
from mapa.spatial.definition.definition_model import CreateDefinition
from mapa.spatial.definition.definition_service import DefinitionService
from mapa.spatial.layer.layer_model import CreateLayer
from mapa.spatial.layer.layer_service import LayerService
from mapa.spatial.layer_definition.layer_definition_service import \
    LayerDefinitionService
from mapa.spatial.layer_hook.layer_hook_service import LayerHookService
from mapa.spatial.map.map_model import CreateMap, Types
from mapa.spatial.map.map_service import MapService
from mapa.spatial.map_base_layer.map_base_layer_service import \
    MapBaseLayerService
from mapa.spatial.map_layer.map_layer_model import CreateMapLayer
from mapa.spatial.map_layer.map_layer_service import MapLayerService
from mapa.spatial.namespace.namespace_model import CreateNamespace
from mapa.spatial.namespace.namespace_service import NamespaceService
from mapa.spatial.reference.reference_model import CreateReference
from mapa.spatial.reference.reference_service import ReferenceService
from nanoid import generate

from .conftest import GatewayFixture, ManageFixture, SpatialFixture
from .data import (generate_authorization_info, generate_field_params_list,
                   generate_geometry_field_param, generate_layer_definition,
                   generate_layer_hook, generate_map_base_layer,service_host,
                   generate_params, generate_reference, map_base_layer_select,
                   map_info_select, tenant_id)


async def create_services(fixture: SpatialFixture) -> Dict[str, Any]:
    """"Create All Services"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True
    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async)

    fixture_gateway = GatewayFixture()
    initialized_gateway = await fixture_gateway.create_test_data()
    assert initialized_gateway is True
    async_db_gateway = fixture_gateway.create_db_instance(
        fixture_gateway.db_url_async)

    connection_info_service = ConnectionInfoService(async_db)
    gateway_api_service = GatewayApiService(async_db_gateway)
    route_service = RouteService(async_db_gateway)
    integration_service = IntegrationService(async_db_gateway,route_service,connection_info_service)

    layer_definition_service = LayerDefinitionService(async_db)

    reference_service= ReferenceService(async_db)
    bookmark_service= BookmarkService(async_db)
    map_base_layer_service= MapBaseLayerService(async_db)

    layer_hook_service= LayerHookService(async_db)
    
    return {

        "map_service": MapService(async_db, route_service,reference_service,bookmark_service,map_base_layer_service),
        "connection_info_service": connection_info_service,
        "gateway_api_service": gateway_api_service,
        "integration_service": integration_service,
        "route_service": route_service,
        "namespace_service": NamespaceService(async_db),
        "connection_service": ConnectionService(async_db),
        "layer_service": LayerService(async_db, layer_definition_service),
        "layer_definition_service": LayerDefinitionService(async_db),
        "definition_service": DefinitionService(async_db,layer_definition_service,layer_hook_service),
        "map_layer_service": MapLayerService(async_db),
        "reference_service": reference_service,
        "bookmark_service": bookmark_service,
        "map_base_layer_service": map_base_layer_service,
        "base_layer_service": BaseLayerService(async_db),
        "layer_hook_service": LayerHookService(async_db),
    }


@pytest.mark.asyncio
async def test_create_service(fixture: SpatialFixture):
    """Service"""
    services = await create_services(fixture)

    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    integration_service: IntegrationService = services["integration_service"]
    route_service: RouteService = services["route_service"]

    namespace_service: NamespaceService = services["namespace_service"]
    map_service: MapService = services["map_service"]
    connection_service: ConnectionService = services["connection_service"]

    layer_service: LayerService = services["layer_service"]
    layer_definition_service: LayerDefinitionService = services["layer_definition_service"]

    definition_service: DefinitionService = services["definition_service"]

    map_layer_service: MapLayerService = services["map_layer_service"]

    reference_service: ReferenceService = services["reference_service"]

    bookmark_service: BookmarkService = services["bookmark_service"]
    base_layer_service: BaseLayerService = services["base_layer_service"]
    map_base_layer_service: MapBaseLayerService = services["map_base_layer_service"]

    layer_hook_service: LayerHookService = services["layer_hook_service"]

    assert layer_hook_service is not None

    assert map_base_layer_service is not None
    assert base_layer_service is not None

    assert bookmark_service is not None

    assert reference_service is not None

    assert map_layer_service is not None

    assert definition_service is not None

    assert layer_service is not None
    assert layer_definition_service is not None

    assert connection_info_service is not None

    assert gateway_api_service is not None
    assert integration_service is not None
    assert route_service is not None

    assert namespace_service is not None
    assert map_service is not None
    assert connection_service is not None


@pytest.mark.asyncio
async def test_get_map_full(fixture: SpatialFixture):
    """MapService Crud Test"""
    services = await create_services(fixture)

    connection_info_service: ConnectionInfoService = services["connection_info_service"]

    gateway_api_service: GatewayApiService = services["gateway_api_service"]
    integration_service: IntegrationService = services["integration_service"]
    route_service: RouteService = services["route_service"]

    namespace_service: NamespaceService = services["namespace_service"]
    map_service: MapService = services["map_service"]
    connection_service: ConnectionService = services["connection_service"]

    layer_service: LayerService = services["layer_service"]
    layer_definition_service: LayerDefinitionService = services["layer_definition_service"]

    definition_service: DefinitionService = services["definition_service"]

    map_layer_service: MapLayerService = services["map_layer_service"]

    reference_service: ReferenceService = services["reference_service"]

    bookmark_service: BookmarkService = services["bookmark_service"]

    base_layer_service: BaseLayerService = services["base_layer_service"]
    map_base_layer_service: MapBaseLayerService = services["map_base_layer_service"]

    layer_hook_service: LayerHookService = services["layer_hook_service"]

    assert layer_hook_service is not None

    assert map_base_layer_service is not None
    assert base_layer_service is not None

    assert bookmark_service is not None

    assert reference_service is not None

    assert map_layer_service is not None

    assert definition_service is not None

    assert layer_service is not None
    assert layer_definition_service is not None

    assert connection_info_service is not None

    assert gateway_api_service is not None
    assert integration_service is not None
    assert route_service is not None

    assert namespace_service is not None
    assert map_service is not None
    assert connection_service is not None

    # User eklenir.
    # user_data = await user_service.create(CreateUser(
    #     name=f"Test_user_book", surname="Test_user_book",
    #     email=f"test_book@gmail.com", password="1123124",
    #     subject_id="1123123", phone="1"), str(tenant_id))
    # assert user_data is not None

    # auth eklenir
    auth_info = await connection_info_service.create(CreateConnectionInfo(
        name="geoserver auth",
        description="geoserver auth",
        params=generate_authorization_info().model_dump(),
        type=ConnectionInfoTypes.AUTHENTICATION
    ), tenant_id=tenant_id)

    # arcmap api eklenir
    arcmap_api = await gateway_api_service.create(CreateGatewayApi(
        name="arcmap Api",
        type=ApiTypes.HTTP,
        path="arcmapapi",
        identifier="https://api.arcmapapi",
    ), tenant_id=tenant_id)

    # arcmap api için wms integration eklenir
    arcmap_wms_integration = await integration_service.create(CreateIntegration(description="arcmap wms",
                                                                                name="arcmap wms",
                                                                                type=IntegrationTypes.HTTP_BACKEND,
                                                                                gateway_api_id=arcmap_api.id,
                                                                                context={},
                                                                                connection=HttpBackendConnection(method="GET", endpoint="https://yoltest.kgm.gov.tr/arcgis/services/MVAS/MVAS_MVS/MapServer/WMSServer").model_dump(),default_route=False,default_route_path= "",default_route_methods=[]), tenant_id=tenant_id)

    # arcmap api için wms integration - route ilişkisi eklenir
    arcmap_wms_route = await route_service.create(CreateRoute(description="arcmap route wms",
                                                              path="arcmapwms",
                                                              method_type=MethodTypes.GET,
                                                              gateway_api_id=arcmap_api.id,
                                                              integration_id=arcmap_wms_integration.id), tenant_id=tenant_id)

    # arcmap api için wfs integration eklenir
    arcmap_wfs_integration = await integration_service.create(CreateIntegration(description="arcmap wfs",
                                                                                name="arcmap wfs",
                                                                                type=IntegrationTypes.HTTP_BACKEND,
                                                                                gateway_api_id=arcmap_api.id,
                                                                                context={},
                                                                                connection=HttpBackendConnection(method="GET", endpoint="https://yoltest.kgm.gov.tr/arcgis/services/MVAS/MVAS_MVS/MapServer/WFSServer").model_dump(),default_route=False,default_route_path= "",default_route_methods=[]), tenant_id=tenant_id)

    # arcmap api için wfs integration - route ilişkisi eklenir
    arcmap_wfs_route = await route_service.create(CreateRoute(description="arcmap route wfs",
                                                              path="arcmapwfs",
                                                              method_type=MethodTypes.GET,
                                                              gateway_api_id=arcmap_api.id,
                                                              integration_id=arcmap_wfs_integration.id), tenant_id=tenant_id)

    # geoserver api eklenir
    geoserver_api = await gateway_api_service.create(CreateGatewayApi(
        name="geoserver Api",
        type=ApiTypes.HTTP,
        path="geoserverapi",
        identifier="https://api.geoserverapi",
    ), tenant_id=tenant_id)

    # geoserver api için wms integration eklenir
    geoserver_wms_integration = await integration_service.create(CreateIntegration(description="geoserver wms",
                                                                                   name="geoserver wms",
                                                                                   type=IntegrationTypes.HTTP_BACKEND,
                                                                                   gateway_api_id=geoserver_api.id,
                                                                                   connection_info_id=auth_info.id,
                                                                                   context={},
                                                                                   connection=HttpBackendConnection(method="GET", endpoint="https://cbsservis.kgm.gov.tr/geoserver/btm/ows").model_dump(),default_route=False,default_route_path= "",default_route_methods=[]), tenant_id=tenant_id)

    # geoserver api için wms integration - route ilişkisi eklenir
    geoserver_wms_route = await route_service.create(CreateRoute(description="geoserver route wms",
                                                                 path="geoserverwms",
                                                                 method_type=MethodTypes.GET,
                                                                 gateway_api_id=geoserver_api.id,
                                                                 integration_id=geoserver_wms_integration.id), tenant_id=tenant_id)

    # geoserver api için wfs integration eklenir
    geoserver_wfs_integration = await integration_service.create(CreateIntegration(description="geoserver wfs",
                                                                                   name="geoserver wfs",
                                                                                   type=IntegrationTypes.HTTP_BACKEND,
                                                                                   gateway_api_id=geoserver_api.id,
                                                                                   connection_info_id=auth_info.id,
                                                                                   context={},
                                                                                   connection=HttpBackendConnection(method="GET", endpoint="https://cbsservis.kgm.gov.tr/geoserver/btm/ows").model_dump(),default_route=False,default_route_path= "",default_route_methods=[]), tenant_id=tenant_id)

    # geoserver api için wfs integration - route ilişkisi eklenir
    geoserver_wfs_route = await route_service.create(CreateRoute(description="geoserver route wfs",
                                                                 path="geoserverwfs",
                                                                 method_type=MethodTypes.GET,
                                                                 gateway_api_id=geoserver_api.id,
                                                                 integration_id=geoserver_wfs_integration.id), tenant_id=tenant_id)


# namespace eklenir
    namespace = await namespace_service.create(CreateNamespace(
        name="info_namespace",
        title="map testi için",
        description="map testi için",
        identifier="https://namespace_identifier_map_testi"), tenant_id=tenant_id)


# map eklenir
    map = await map_service.create(CreateMap(
        namespace_id=namespace.id,
        name="map_test",
        title="map_test_title",
        description="map_test_desc",
        initial_extent="97.65656917606952;37.86541500399325;75.1803520939344;19.7160900653360" +
        str(random.randint(0, 10)),
        full_extent="46.333723794096386;46.29575588844355;23.85750671196024;30.02581711044706" +
        str(random.randint(0, 10)),
        srid=SridTypes.EPSG_3857,
        zoom=16,
        widget_types=[Types(key=MapWidgetType.AttributeTable), Types(
            key=MapWidgetType.Bookmark), Types(key=MapWidgetType.Info)]
    ), tenant_id=tenant_id)


# arcmap connection eklenir
    arcmap_connection = await connection_service.create(CreateConnection(
        route_params=[RouteParams(type=RouteParamsTypes.Wms, route_id=str(arcmap_wms_route.id)),
                      RouteParams(type=RouteParamsTypes.Feature, route_id=str(arcmap_wfs_route.id))],
        description="arcmap_connection_desc",
        name="arcmap_connection",
        type=ConnectionTypes.External
    ), tenant_id=tenant_id)

# geoserver connection eklenir
    geoserver_connection = await connection_service.create(CreateConnection(
        route_params=[RouteParams(type=RouteParamsTypes.Wms, route_id=str(geoserver_wms_route.id)),
                      RouteParams(type=RouteParamsTypes.Feature, route_id=str(geoserver_wfs_route.id))],
        description="geoserver_connection_desc",
        name="geoserver_connection",
        type=ConnectionTypes.External
    ), tenant_id=tenant_id)


# 2 adet arcmap default layer eklenir

    default_layer_arcmap_1 = await layer_service.create(
        CreateLayer(name="default_layer_arcmap_1",
                    description="default_layer_arcmap_1",
                    title="default_layer_arcmap_1",
                    code="1",
                    default_extent="",
                    max_scale=random.randint(100, 10000),
                    min_scale=random.randint(100, 10000),
                    opacity=random.randint(0, 1),
                    timer=False,
                    visible=True,
                    connection_id=arcmap_connection.id,
                    field_params=generate_field_params_list(),
                    geometry_field_param=generate_geometry_field_param(),
                    data_type=DataType.Png,
                    key_field="id",
                    target_namespace=None,
                    type_name="test:layer",
                    ), tenant_id=tenant_id)

    default_layer_arcmap_2 = await layer_service.create(
        CreateLayer(name="default_layer_arcmap_2",
                    description="default_layer_arcmap_2",
                    title="default_layer_arcmap_2",
                    code="2",
                    default_extent="",
                    max_scale=random.randint(100, 10000),
                    min_scale=random.randint(100, 10000),
                    opacity=random.randint(0, 1),
                    timer=False,
                    visible=True,
                    connection_id=arcmap_connection.id,
                    field_params=generate_field_params_list(),
                    geometry_field_param=generate_geometry_field_param(),
                    data_type=DataType.Png,
                    key_field="id",
                    target_namespace=None,
                    type_name="test:layer",
                    ), tenant_id=tenant_id)


# 2 adet geoserver default layer eklenir

    default_layer_geoserver_1 = await layer_service.create(
        CreateLayer(name="default_layer_geoserver_1",
                    description="default_layer_geoserver_1",
                    title="default_layer_geoserver_1",
                    code="1",
                    default_extent="",
                    max_scale=random.randint(100, 10000),
                    min_scale=random.randint(100, 10000),
                    opacity=random.randint(0, 1),
                    timer=False,
                    visible=True,
                    connection_id=geoserver_connection.id,
                    field_params=generate_field_params_list(),
                    geometry_field_param=generate_geometry_field_param(),
                    data_type=DataType.Png,
                    key_field="id",
                    target_namespace=None,
                    type_name="test:layer",
                    ), tenant_id=tenant_id)

    default_layer_geoserver_2 = await layer_service.create(
        CreateLayer(name="default_layer_geoserver_2",
                    description="default_layer_geoserver_2",
                    title="default_layer_geoserver_2",
                    code="2",
                    default_extent="",
                    max_scale=random.randint(100, 10000),
                    min_scale=random.randint(100, 10000),
                    opacity=random.randint(0, 1),
                    timer=False,
                    visible=True,
                    connection_id=geoserver_connection.id,
                    field_params=generate_field_params_list(),
                    geometry_field_param=generate_geometry_field_param(),
                    data_type=DataType.Png,
                    key_field="id",
                    target_namespace=None,
                    type_name="test:layer",
                    ), tenant_id=tenant_id)


# 2 adet arcmap definition layer eklenir

    definition_layer_arcmap_1 = await definition_service.create(
        CreateDefinition(
            title="definition_layer_arcmap_1",
            default_extent="",
            max_scale=random.randint(100, 10000),
            min_scale=random.randint(100, 10000),
            opacity=random.randint(0, 1),
            timer=False,
            is_attribute_panel=True,
            organization_geo_constraint=False,
            is_base_layer=True,
            edit_snap_scale=random.randint(100, 10000),
            data_type=DataType.Png,
            key_field="id",
            target_namespace=None,
            type_name="test:layer",
            field_params=generate_field_params_list()), tenant_id=tenant_id)

    definition_layer_arcmap_2 = await definition_service.create(
        CreateDefinition(
            title="definition_layer_arcmap_2",
            default_extent="",
            max_scale=random.randint(100, 10000),
            min_scale=random.randint(100, 10000),
            opacity=random.randint(0, 1),
            timer=False,
            is_attribute_panel=True,
            organization_geo_constraint=False,
            is_base_layer=True,
            edit_snap_scale=random.randint(100, 10000),
            data_type=DataType.Png,
            key_field="id",
            target_namespace=None,
            type_name="test:layer",
            field_params=generate_field_params_list()), tenant_id=tenant_id)


# 2 adet geoserver definition layer eklenir

    definition_layer_geoserver_1 = await definition_service.create(
        CreateDefinition(
            title="definition_layer_geoserver_1",
            default_extent="",
            max_scale=random.randint(100, 10000),
            min_scale=random.randint(100, 10000),
            opacity=random.randint(0, 1),
            timer=False,
            is_attribute_panel=True,
            organization_geo_constraint=False,
            is_base_layer=True,
            edit_snap_scale=random.randint(100, 10000),
            data_type=DataType.Png,
            key_field="id",
            type_name="test:layer",
            target_namespace=None,
            field_params=generate_field_params_list()), tenant_id=tenant_id)

    definition_layer_geoserver_2 = await definition_service.create(
        CreateDefinition(
            title="definition_layer_geoserver_2",
            default_extent="",
            max_scale=random.randint(100, 10000),
            min_scale=random.randint(100, 10000),
            opacity=random.randint(0, 1),
            timer=False,
            is_attribute_panel=True,
            organization_geo_constraint= False,
            is_base_layer=True,
            edit_snap_scale=random.randint(100, 10000),
            data_type=DataType.Png,
            key_field="id",
            target_namespace=None,
            type_name="test:layer",
            field_params=generate_field_params_list()), tenant_id=tenant_id)


# arcmap layer ve definition ilişkisi kurulur

    default_definition_arcmap_1 = await layer_definition_service.create(generate_layer_definition(default_layer_arcmap_1.id, definition_layer_arcmap_1.id),
                                                                        tenant_id=tenant_id)

    default_definition_arcmap_2 = await layer_definition_service.create(generate_layer_definition(default_layer_arcmap_2.id, definition_layer_arcmap_2.id),
                                                                        tenant_id=tenant_id)

# geoserver layer ve definition ilişkisi kurulur

    default_definition_geoserver_1 = await layer_definition_service.create(generate_layer_definition(default_layer_geoserver_1.id, definition_layer_geoserver_1.id),
                                                                           tenant_id=tenant_id)

    default_definition_geoserver_2 = await layer_definition_service.create(generate_layer_definition(default_layer_geoserver_2.id, definition_layer_geoserver_2.id),
                                                                           tenant_id=tenant_id)

# map ve layer ilişkisi kurulur

    map_layer_default_definition_arcmap_1 = await map_layer_service.create(CreateMapLayer(
        name="map_layer_default_definition_arcmap_1",
        order=random.randint(0, 11),
        map_id=map.id,
        layer_definition_id=default_definition_arcmap_1.id,
        params=generate_params()
    ), tenant_id=tenant_id)

    map_layer_default_definition_arcmap_2 = await map_layer_service.create(CreateMapLayer(
        name="map_layer_default_definition_arcmap_2",
        order=random.randint(0, 11),
        map_id=map.id,
        layer_definition_id=default_definition_arcmap_2.id,
        params=generate_params()
    ), tenant_id=tenant_id)

    map_layer_default_definition_geoserver_1 = await map_layer_service.create(CreateMapLayer(
        name="map_layer_default_definition_geoserver_1",
        order=random.randint(0, 11),
        map_id=map.id,
        layer_definition_id=default_definition_geoserver_1.id,
        params=generate_params()
    ), tenant_id=tenant_id)

    map_layer_default_definition_geoserver_2 = await map_layer_service.create(CreateMapLayer(
        name="map_layer_default_definition_geoserver_2",
        order=random.randint(0, 11),
        map_id=map.id,
        layer_definition_id=default_definition_geoserver_2.id,
        params=generate_params()
    ), tenant_id=tenant_id)

    # Reference Listesi eklenir
    lst: List[CreateReference] = generate_reference()
    el_count = len(lst)
    task_list = (reference_service.create(lst[i], tenant_id=fixture.tenant_id)
                 for i in range(0, el_count))
    items = await asyncio.gather(*task_list)
    assert items is not None
    assert len(items) == el_count

    # Bookmark Listesi eklenir
    bookmark_data = await bookmark_service.create(str(user_data.id), CreateBookmark(user_id=user_data.id,
                                                                                    map_id=map.id,
                                                                                    name="Full_Test_name_book" +
                                                                                    generate(
                                                                                        size=4),
                                                                                    location=str(random.uniform(3624500.449655232, 3634500.449655232)) + ";" + str(
                                                                                        random.uniform(4858253.604920756, 4868253.604920756)) + ";" + str(3857) + ";" + str(random.randint(1, 20)),
                                                                                    thumbnail="Full_TTest_thumbnail_book"+generate(size=4),), str(tenant_id))
    assert bookmark_data is not None

    # base-layer eklenir
    base_layer_data_1 = await base_layer_service.create(CreateBaseLayer(
        type=BaseLayerTypes.WebMapService, connection=BaseLayerConnection(name='test__', thumbnail="base64", tiles=['https://mt0.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                                                    'https://mt1.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                                                    'https://mt2.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                                                    'https://mt3.google.com/vt/lyrs=y&z={z}&x={x}&y={y}'], tile_size=256)
    ), tenant_id=tenant_id)
    assert base_layer_data_1 is not None

    # base-layer eklenir
    base_layer_data_2 = await base_layer_service.create(CreateBaseLayer(
        type=BaseLayerTypes.VectorTileService, connection=BaseLayerConnection(name='test__2', thumbnail="2", tiles=['https://mt0.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                                                    'https://mt1.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                                                    'https://mt2.google.com/vt/lyrs=y&z={z}&x={x}&y={y}',
                                                                                                                    'https://mt3.google.com/vt/lyrs=y&z={z}&x={x}&y={y}'], tile_size=256)
    ), tenant_id=tenant_id)
    assert base_layer_data_2 is not None

    # map - base - layer eklenir
    map_base_layer_data_1 = await map_base_layer_service.create(
        generate_map_base_layer(map.id, base_layer_data_1.id), tenant_id=tenant_id)
    assert map_base_layer_data_1 is not None

    # map - base - layer eklenir
    map_base_layer_data_2 = await map_base_layer_service.create(
        generate_map_base_layer(map.id, base_layer_data_2.id), tenant_id=tenant_id)
    assert map_base_layer_data_2 is not None

    # Layer Hook eklinir
    layer_hook_data_get = await layer_hook_service.create(generate_layer_hook(
        arcmap_wms_route.id, default_definition_geoserver_1.id, hook_operation_type=HookOperationType.GET), tenant_id=tenant_id)

    layer_hook_data_post = await layer_hook_service.create(generate_layer_hook(
        arcmap_wfs_route.id, default_definition_geoserver_1.id, hook_operation_type=HookOperationType.POST), tenant_id=tenant_id)

    layer_hook_data_put = await layer_hook_service.create(generate_layer_hook(
        geoserver_wms_route.id, default_definition_geoserver_1.id, hook_operation_type=HookOperationType.PUT), tenant_id=tenant_id)

    # Sorgulama işlemleri yapılır
    query_map_info: QueryArgs = QueryArgs(where=[
        Filter(field="id", op=FilterOp.EQUAL, value=map.id)
    ], select=map_info_select)

    map_info = await map_service.paging(query_map_info, tenant_id=tenant_id)

    assert len(map_info.items) == 1

    full_map = await map_service.get_map_full_info(map_info.items,service_host,tenant_id)

    assert len(full_map) == 1
