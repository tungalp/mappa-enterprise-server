from typing import List

from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.result import PagingResult
from mapa.spatial.ent_models import IntegrationTypes, Route, SpatialAdhocBackend, SpatialBackendType, SpatialExternalBackend, SpatialServiceType
from mapa.spatial.bookmark.bookmark_model import Bookmark
from mapa.spatial.connection.connection_model import Connection
from mapa.spatial.constant import RouteParamsTypes
from mapa.spatial.definition.definition_model import Definition
from mapa.spatial.layer.layer_model import Layer
from mapa.spatial.layer_hook.layer_hook_model import LayerHook
from mapa.spatial.map.map_model import CreateMap, Map, UpdateAllMap, UpdateMap
from mapa.spatial.map.map_repository import MapRepository
from mapa.spatial.map_layer.map_layer_model import MapLayer
from mapa.spatial.messaging.producer.service_messenger import ServiceMessenger
from mapa.spatial.models.layer_gateway_params_model import LayerGatewayParams
from mapa.spatial.models.layer_hooks_gateway_params_model import LayerHookGatewayParams
from mapa.spatial.models.merge_layer_model import MergeLayer
from mapa.spatial.bookmark.bookmark_service import BookmarkService
from mapa.spatial.map_base_layer.map_base_layer_service import MapBaseLayerService
from mapa.spatial.map_base_layer.map_base_layer_model import MapBaseLayer
from mapa.spatial.reference.reference_model import Reference
from mapa.spatial.reference.reference_service import ReferenceService
from mapa.spatial.ent_models import Tenant
from uuid import uuid4


class MapService(
    BaseEntityService[MapRepository, Map, CreateMap, UpdateMap, UpdateAllMap]
):
    """Map Servisi"""

    def __init__(
        self,
        async_db: AsyncDatabase,
        reference_service: ReferenceService,
        bookmark_service: BookmarkService,
        map_base_layer_service: MapBaseLayerService,
        messenger: ServiceMessenger,
    ) -> None:
        self.async_db = async_db
        self._reference_service = reference_service
        self._bookmark_service = bookmark_service
        self._map_base_layer_service = map_base_layer_service
        self.messenger = messenger
        super().__init__(async_db, MapRepository, Map)

    async def get_map_full_info(
        self,
        maps: List[Map],
        service_host: str,
        tenant_id: str | None = None,
        user_id: str | None = None,
    ) -> List[Map]:

        tenant = await self.get_tenant(tenant_id)

        for map in maps:
            map.merge_layers = []
            if map.map_layers != None:
                for map_layer in map.map_layers:

                    if (
                        map_layer
                        and map_layer.layer_definition
                        and map_layer.layer_definition.layer
                        and map_layer.layer_definition.layer.connection
                    ):
                        gateway_params = await self.get_gateway_params(
                            map_layer.layer_definition.layer.connection, tenant_id
                        )
                        if gateway_params != None:
                            map_layer.layer_definition.layer.layer_gateway_params = (
                                gateway_params
                            )

                    if (
                        map_layer.layer_definition is not None
                        and map_layer.layer_definition.layer_hooks is not None
                        and len(map_layer.layer_definition.layer_hooks) > 0
                    ):
                        layer_hooks_gateway_params = (
                            await self.get_layer_hooks_gateway_params(
                                map_layer.layer_definition.layer_hooks, tenant_id
                            )
                        )
                        map_layer.layer_definition.layer_hooks_gateway_params = (
                            layer_hooks_gateway_params
                        )

                    merged_layer = await self.get_merge_layer(
                        map_layer, service_host, tenant.name
                    )
                    if merged_layer != None:
                        map.merge_layers.append(merged_layer)
            references = await self.get_reference(tenant_id)
            if references:
                map.references = references.items

            bookmarks = await self.get_bookmark(map, tenant_id, user_id)
            if bookmarks:
                map.bookmarks = bookmarks.items

            map_base_layers = await self.get_map_base_layers(map, tenant_id)
            if map_base_layers:
                map.map_base_layers = map_base_layers.items
            map.merge_layers.sort(
                reverse=True, key=lambda element: element.parent_id is not None
            )
            map.merge_layers.reverse()
        return maps

    async def get_tenant(
        self, tenant_id: str | None = None, fields: list[str] = []
    ) -> Tenant:
        tenant = await self.messenger.tenant_get(tenant_id, fields)  # type: ignore
        tenant = Tenant.model_validate(tenant) 
        return tenant

    async def get_map_base_layers(
        self, map: Map, tenant_id: str | None = None
    ) -> PagingResult[MapBaseLayer]:
        query_map_base_layer: QueryArgs = QueryArgs(
            where=[Filter(field="map_id", op=FilterOp.EQUAL, value=map.id)],
            select=[
                "id",
                "order",
                "map_id",
                "base_layer_id",
                "base_layer.id",
                "base_layer.type",
                "base_layer.connection",
            ],
            limit=0,
            offset=0,
        )

        map_base_layers: PagingResult[MapBaseLayer] = (
            await self._map_base_layer_service.paging(query_map_base_layer, tenant_id)
        )
        return map_base_layers

    async def get_bookmark(
        self, map: Map, tenant_id: str | None = None, user_id: str | None = None
    ) -> PagingResult[Bookmark]:
        query_bookmarks: QueryArgs = QueryArgs(
            where=[Filter(field="map_id", op=FilterOp.EQUAL, value=map.id)],
            limit=0,
            offset=0,
        )
        bookmarks: PagingResult[Bookmark] = await self._bookmark_service.paging(
            query_bookmarks, str(user_id) if user_id else user_id, tenant_id
        )

        return bookmarks

    async def get_reference(
        self, tenant_id: str | None = None
    ) -> PagingResult[Reference]:
        query_reference: QueryArgs = QueryArgs(
            where=[Filter(field="id", op=FilterOp.NOT_NULL, value=uuid4())],
            limit=0,
            offset=0,
        )
        references: PagingResult[Reference] = await self._reference_service.paging(
            query_reference, tenant_id
        )

        return references

    async def get_merge_layer(
        self, map_layer: MapLayer, service_host: str, tenant_name: str
    ) -> MergeLayer | None:
        if map_layer:
            definition = (
                map_layer.layer_definition.definition
                if map_layer.layer_definition
                else None
            )
            layer = (
                map_layer.layer_definition.layer if map_layer.layer_definition else None
            )
            return generated_merge_definition(
                map_layer, service_host, tenant_name, layer, definition
            )

    async def get_gateway_params(
        self, conn: Connection, tenant_id: str | None = None
    ) -> LayerGatewayParams:

        layer_gateway_params = LayerGatewayParams()
        if conn and conn.route_params:
            params = conn.route_params

            for param in params:
                if param.route_id:
                    query_route: QueryArgs = QueryArgs(
                        limit=0,
                        offset=0,
                        where=[
                            Filter(field="id", op=FilterOp.EQUAL, value=param.route_id),
                            Filter(
                                field="integration.type",
                                op=FilterOp.EQUAL,
                                value=IntegrationTypes.SPATIAL_BACKEND,
                            ),
                        ],
                        select=[
                            "id",
                            "created_at",
                            "description",
                            "method_type",
                            "path",
                            "query",
                            "cache_timeout",
                            "rate_limit",
                            "rate_second",
                            "retry_count",
                            "retry_millisecond",
                            "full_logging",
                            "gateway_api_id",
                            "integration_id",
                            "scope",
                            "integration.id",
                            "integration.name",
                            "integration.gateway_api_id",
                            "integration.timeout_in_millis",
                            "integration.type",
                            "integration.connection",
                            "integration.context",
                            "gateway_api.id",
                            "gateway_api.name",
                            "gateway_api.tenant_id",
                            "gateway_api.type",
                            "gateway_api.path",
                            "gateway_api.identifier",
                        ],
                    )

                    routes = await self.messenger.route_paging(query_route.to_serialize(), tenant_id=tenant_id)  # type: ignore
                    route = routes["items"]
                    route = [Route.model_validate(r) for r in route] if route else []
                    if len(route) == 1:
                        gateway_connection = route[0].integration.connection  # type: ignore
                        gateway_full_path = route[0].gateway_api["path"] + "/" + route[0].path  # type: ignore

                        # Backend Tipine göre model oluşturulur
                        backend_type = gateway_connection["backend"]["type"]
                        external = None
                        adhoc = None
                        if backend_type == SpatialBackendType.External:
                            external = SpatialExternalBackend(
                                **gateway_connection["backend"]
                            )
                        elif backend_type == SpatialBackendType.Adhoc:
                            adhoc = SpatialAdhocBackend(**gateway_connection["backend"])

                        if (
                            param.type == RouteParamsTypes.Wms
                            and gateway_connection["service_type"]
                            == SpatialServiceType.WMS
                        ):
                            if external is not None:
                                layer_gateway_params.wms_path = gateway_full_path
                                layer_gateway_params.wms_endpoint = external.endpoint
                                layer_gateway_params.wms_method_type = external.method
                                layer_gateway_params.wms_server_type = (
                                    external.server_type
                                )
                                layer_gateway_params.wms_backend_type = external.type
                                layer_gateway_params.wms_service_format = external.service_format
                            elif adhoc is not None:
                                layer_gateway_params.wms_sql = adhoc.sql
                                layer_gateway_params.wms_geometry_column = (
                                    adhoc.geometry_column
                                )

                        if (
                            param.type == RouteParamsTypes.Tile
                            and gateway_connection["service_type"]
                            == SpatialServiceType.Tile
                        ):
                            if external is not None:
                                layer_gateway_params.tile_path = gateway_full_path
                                layer_gateway_params.tile_endpoint = external.endpoint
                                layer_gateway_params.tile_method_type = external.method
                                layer_gateway_params.tile_server_type = (
                                    external.server_type
                                )
                                layer_gateway_params.tile_backend_type = external.type
                                layer_gateway_params.tile_service_format = external.service_format
                            elif adhoc is not None:
                                layer_gateway_params.tile_sql = adhoc.sql
                                layer_gateway_params.tile_geometry_column = (
                                    adhoc.geometry_column
                                )

                        if (
                            param.type == RouteParamsTypes.Feature
                            and gateway_connection["service_type"]
                            == SpatialServiceType.Feature
                        ):
                            if external is not None:
                                layer_gateway_params.feature_path = gateway_full_path
                                layer_gateway_params.feature_endpoint = (
                                    external.endpoint
                                )
                                layer_gateway_params.feature_method_type = (
                                    external.method
                                )
                                layer_gateway_params.feature_server_type = (
                                    external.server_type
                                )
                                layer_gateway_params.feature_backend_type = (
                                    external.type
                                )
                                layer_gateway_params.feature_service_format = (external.service_format)
                            elif adhoc is not None:
                                layer_gateway_params.feature_sql = adhoc.sql
                                layer_gateway_params.feature_geometry_column = (
                                    adhoc.geometry_column
                                )

                        if (
                            param.type == RouteParamsTypes.Transaction
                            and gateway_connection["service_type"]
                            == SpatialServiceType.Transaction
                        ):
                            if external is not None:
                                layer_gateway_params.transaction_path = (
                                    gateway_full_path
                                )
                                layer_gateway_params.transaction_endpoint = (
                                    external.endpoint
                                )
                                layer_gateway_params.transaction_method_type = (
                                    external.method
                                )
                                layer_gateway_params.transaction_server_type = (
                                    external.server_type
                                )
                                layer_gateway_params.transaction_backend_type = (
                                    external.type
                                )
                                layer_gateway_params.transaction_service_format = (external.service_format)
                            elif adhoc is not None:
                                layer_gateway_params.transaction_sql = adhoc.sql
                                layer_gateway_params.transaction_geometry_column = (
                                    adhoc.geometry_column
                                )

        return layer_gateway_params

    async def get_layer_hooks_gateway_params(
        self, layer_hooks: List[LayerHook], tenant_id: str | None = None
    ) -> List[LayerHookGatewayParams]:

        layer_hooks_gateway_params = []
        for layer_hook in layer_hooks:

            if layer_hook.route_id:
                query_route: QueryArgs = QueryArgs(
                    limit=0,
                    offset=0,
                    where=[
                        Filter(field="id", op=FilterOp.EQUAL, value=layer_hook.route_id)
                    ],
                    select=[
                        "id",
                        "created_at",
                        "description",
                        "method_type",
                        "path",
                        "query",
                        "cache_timeout",
                        "rate_limit",
                        "rate_second",
                        "retry_count",
                        "retry_millisecond",
                        "full_logging",
                        "gateway_api_id",
                        "integration_id",
                        "scope",
                        "integration.id",
                        "integration.name",
                        "integration.gateway_api_id",
                        "integration.timeout_in_millis",
                        "integration.type",
                        "integration.connection",
                        "integration.context",
                        "gateway_api.id",
                        "gateway_api.name",
                        "gateway_api.tenant_id",
                        "gateway_api.type",
                        "gateway_api.path",
                        "gateway_api.identifier",
                    ],
                )

                routes = await self.messenger.route_paging(query_route.to_serialize(), tenant_id=tenant_id)  # type: ignore
                route = routes["items"]
                route = [Route.model_validate(r) for r in route] if route else []
                if len(route) == 1:
                    gateway_connection = route[0].integration.connection  # type: ignore
                    full_path = route[0].gateway_api["path"] + "/" + route[0].path  # type: ignore

                    layer_hooks_gateway_params.append(
                        LayerHookGatewayParams(
                            route_id=layer_hook.route_id,
                            layer_definition_id=layer_hook.layer_definition_id,
                            widget_name=layer_hook.widget_name,
                            hook_operation_type=layer_hook.hook_operation_type,
                            full_path=full_path,
                            endpoint=gateway_connection["endpoint"],
                            method_type=gateway_connection["method"],
                        )
                    )

        return layer_hooks_gateway_params


def generated_merge_definition(
    map_layer: MapLayer,
    service_host: str,
    tenant_name: str,
    layer: Layer | None = None,
    definition: Definition | None = None,
) -> MergeLayer:
    merged_layer = MergeLayer(
        # MapLayer Props
        id=map_layer.id,
        map_layer_name=map_layer.name,
        parent_id=map_layer.parent_id,
        order=map_layer.order,
        children=None,
        # LayerDefinition Props
        layer_hooks=(
            map_layer.layer_definition.layer_hooks
            if map_layer.layer_definition
            else None
        ),
        layer_hooks_gateway_params=(
            map_layer.layer_definition.layer_hooks_gateway_params
            if map_layer.layer_definition
            else None
        ),
        # Merge Props
        title=definition.title if definition else (layer.title if layer else None),
        default_extent=(
            definition.default_extent
            if definition
            else (layer.title if layer else None)
        ),
        max_scale=(
            definition.max_scale if definition else (layer.max_scale if layer else None)
        ),
        min_scale=(
            definition.min_scale if definition else (layer.min_scale if layer else None)
        ),
        opacity=(
            definition.opacity if definition else (layer.opacity if layer else None)
        ),
        timer=definition.timer if definition else (layer.timer if layer else None),
        data_type=(
            definition.data_type if definition else (layer.data_type if layer else None)
        ),
        key_field=(
            definition.key_field if definition else (layer.key_field if layer else None)
        ),
        target_namespace=(
            definition.target_namespace
            if definition
            else (layer.target_namespace if layer else None)
        ),
        type_name=(
            definition.type_name if definition else (layer.type_name if layer else None)
        ),
        style_params=(
            definition.style_params
            if definition
            else (layer.style_params if layer else None)
        ),
        field_params=(
            definition.field_params
            if definition
            else (layer.field_params if layer else None)
        ),
        # Layer Props
        name=layer.name if layer else None,
        code=layer.code if layer else None,
        description=layer.description if layer else None,
        visible=layer.visible if layer else None,
        connection_id=layer.connection_id if layer else None,
        connection=layer.connection if layer else None,
        geometry_field_param=layer.geometry_field_param if layer else None,
        layer_gateway_params=layer.layer_gateway_params if layer else None,
        # Definition Props
        is_attribute_panel=definition.is_attribute_panel if definition else None,
        organization_geo_constraint=(
            definition.organization_geo_constraint if definition else None
        ),
        is_base_layer=definition.is_base_layer if definition else None,
        edit_snap_scale=definition.edit_snap_scale if definition else None,
        topology_rules_params=definition.topology_rules_params if definition else None,
        filter_params=definition.filter_params if definition else None,
        # External Props
        tenant_name=tenant_name,
        service_host=service_host,
    )

    # Map layer üzerinde opacity ve visible bilgisi girildi ise bu bilgiler ezilir
    if map_layer.params != None:
        if map_layer.params.opacity != None:
            merged_layer.opacity = map_layer.params.opacity
        if map_layer.params.visible != None:
            merged_layer.visible = map_layer.params.visible

    # grouplanmış bir katmanda layer name bilgisi yoksa map layer name'i kullanılır
    if merged_layer.name == None:
        merged_layer.name = merged_layer.map_layer_name
        merged_layer.title = merged_layer.map_layer_name
    return merged_layer
