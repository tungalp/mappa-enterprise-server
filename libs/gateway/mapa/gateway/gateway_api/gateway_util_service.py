from uuid import UUID
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.connection_info.connection_info_model import (
    ConnectionInfo,
    CreateConnectionInfo,
)
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService
from mapa.gateway.gateway_api.gateway_api_model import (
    CreateGatewayApi,
    ExportGatewayApi,
    GatewayApi,
)
from mapa.gateway.integration.integration_model import CreateIntegration, Integration
from mapa.gateway.integration.integration_service import IntegrationService
from mapa.gateway.messaging.producer.service_messenger import ServiceMessenger
from mapa.gateway.models import ApiScope, CreateApiScope
from mapa.gateway.parameter_mapping.parameter_mapping_model import (
    CreateParameterMapping,
    ParameterMapping,
)
from mapa.gateway.parameter_mapping.parameter_mapping_service import (
    ParameterMappingService,
)
from mapa.gateway.route.route_model import CreateRoute, Route
from mapa.gateway.route.route_service import RouteService
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService
from mapa.core.data.base_service import BaseService
from typing import Any, Dict, List
from mapa.gateway.constant import ApiTypes, LevelTypes
from mapa.core.data.json_encoder import JsonEncoder
import json
import asyncio


class GatewayUtilService(BaseService):
    """GatewayUtil Servisi"""

    def __init__(
        self,
        gateway_api_service: GatewayApiService,
        route_service: RouteService,
        integration_service: IntegrationService,
        parameter_mapping_service: ParameterMappingService,
        connection_info_service: ConnectionInfoService,
        messenger: ServiceMessenger,
    ) -> None:
        self.gateway_api_service = gateway_api_service
        self.route_service = route_service
        self.integration_service = integration_service
        self.parameter_mapping_service = parameter_mapping_service
        self.connection_info_service = connection_info_service
        self.messenger = messenger
        super().__init__()

    async def count(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        """Sorgu parametrelerine uyan kayıtları sayısını döndürür."""
        return await self.gateway_api_service.count(query_args, tenant_id)

    async def export_gateway_apis(
        self, query_args: QueryArgs, tenant_id: str | None = None
    ) -> List[ExportGatewayApi]:
        exportApis = []
        if query_args.select is None:
            query_args.select = [
                "id",
                "name",
                "description",
                "type",
                "path",
                "identifier",
                "manage_api_id",
                "context",
                "tenant_id",
                "routes.id",
                "routes.tenant_id",
                "routes.description",
                "routes.method_type",
                "routes.path",
                "routes.scope",
                "routes.query",
                "routes.cache_timeout",
                "routes.rate_limit",
                "routes.rate_second",
                "routes.retry_count",
                "routes.retry_millisecond",
                "routes.full_logging",
                "routes.gateway_api_id",
                "routes.integration_id",
            ]

        gateway_apis = await self.gateway_api_service.find(query_args, tenant_id)
        query_args.select = [
            "id",
            "name",
            "description",
            "type",
            "path",
            "identifier",
            "manage_api_id",
            "context",
            "tenant_id",
            "integrations.id",
            "integrations.tenant_id",
            "integrations.name",
            "integrations.description",
            "integrations.timeout_in_millis",
            "integrations.type",
            "integrations.connection",
            "integrations.connection_info_id",
            "integrations.gateway_api_id",
            "integrations.context",
            "integrations.connection_info.id",
            "integrations.connection_info.name",
            "integrations.connection_info.description",
            "integrations.connection_info.params",
            "integrations.connection_info.type",
            "integrations.connection_info.tenant_id",
            "integrations.parameter_mappings.id",
            "integrations.parameter_mappings.status_code",
            "integrations.parameter_mappings.type",
            "integrations.parameter_mappings.param_list",
            "integrations.parameter_mappings.integration_id",
            "integrations.parameter_mappings.tenant_id",
        ]
        gateway_apis_integration = await self.gateway_api_service.find(
            query_args, tenant_id
        )
        integration_map = {api.id: api.integrations for api in gateway_apis_integration}

        for api in gateway_apis:
            api_id = api.id
            api.integrations = integration_map.get(api_id, [])

        for gateway_api in gateway_apis:
            exportApi = generated_export_gateway_api(gateway_api, [])

            query_args_scope: QueryArgs = QueryArgs(
                where=[
                    Filter(
                        field="api_id",
                        op=FilterOp.EQUAL,
                        value=gateway_api.manage_api_id,
                    ),
                ],
                limit=0,
                offset=0,
            )

            manage_api_scopes = await self.messenger.api_scope_paging(
                query_args_scope.to_serialize(), tenant_id
            )

            exportApi.scopes = manage_api_scopes["items"]
            exportApis.append(exportApi)

        return exportApis

    async def import_gateway_apis(
        self, importGatewayApis: List[ExportGatewayApi], tenant_id: str | None = None
    ) -> List[ExportGatewayApi]:
        """Verilen parametrelerdeki gateway apileri içeri aktarır."""

        created_gateway_api_id_list = []
        created_connection_info_id_list = []
        created_integration_id_list = []
        created_route_id_list = []
        created_parameter_mapping_id_list = []
        created_api_scope_id_list = []

        for gateway_api in importGatewayApis:
            try:
                gateway_api = ExportGatewayApi(
                    **json.loads(json.dumps(gateway_api, cls=JsonEncoder))
                )

                # Manage api kontrolu
                manage_api_query = QueryArgs(
                    where=[
                        Filter(field="name", op=FilterOp.EQUAL, value=gateway_api.name),
                        Filter(
                            field="level_type",
                            op=FilterOp.EQUAL,
                            value=LevelTypes.SECOND_PARTY,
                        ),
                        Filter(
                            field="identifier",
                            op=FilterOp.EQUAL,
                            value=gateway_api.identifier,
                        ),
                    ]
                )
                # Gateway api kontrolu
                gateway_api_query = QueryArgs(
                    where=[
                        Filter(field="name", op=FilterOp.EQUAL, value=gateway_api.name),
                        Filter(
                            field="identifier",
                            op=FilterOp.EQUAL,
                            value=gateway_api.identifier,
                        ),
                    ]
                )

                manage_api_count, gateway_api_count = await asyncio.gather(
                    self.messenger.api_count(
                        manage_api_query.to_serialize(), tenant_id
                    ),
                    self.gateway_api_service.count(gateway_api_query, tenant_id),
                )

                if manage_api_count == 0 and gateway_api_count == 0:
                    # Create Manage api and Gateway api
                    create_gateway_api = generate_gateway_api(gateway_api)
                    created_gateway_api = await self.gateway_api_service.create(
                        create_gateway_api, tenant_id
                    )
                    created_gateway_api_id_list.append(created_gateway_api.id)

                    # Create Manage Api Scope
                    if created_gateway_api.manage_api_id:
                        api_id = created_gateway_api.manage_api_id
                        create_manage_api_scope_tasks = [
                            self.messenger.create_api_scope(
                                generate_manage_api_scope(
                                    ApiScope(**scope), api_id
                                ).model_dump(),
                                tenant_id,
                            )
                            for scope in gateway_api.scopes
                        ]
                        created_api_scopes = await asyncio.gather(
                            *create_manage_api_scope_tasks
                        )
                        created_api_scope_id_list.extend(
                            [scope["id"] for scope in created_api_scopes]
                        )

                    connection_info_id_list = []
                    if gateway_api.integrations is not None:
                        for integration in gateway_api.integrations:
                            integration = Integration(**integration.model_dump())

                            if integration.connection_info:
                                integration.connection_info = ConnectionInfo(
                                    **integration.connection_info.model_dump()
                                )
                                # Connection info kontrolu
                                query_args: QueryArgs = QueryArgs(
                                    where=[
                                        Filter(
                                            field="name",
                                            op=FilterOp.EQUAL,
                                            value=integration.connection_info.name,
                                        )
                                    ]
                                )

                                connection_info = (
                                    await self.connection_info_service.find_one(
                                        query_args, tenant_id
                                    )
                                )
                                if connection_info is None:
                                    # Create Connection Info
                                    create_connection_info = generate_connection_info(
                                        integration.connection_info
                                    )
                                    connection_info = (
                                        await self.connection_info_service.create(
                                            create_connection_info, tenant_id
                                        )
                                    )
                                    connection_info_id_list.append(connection_info.id)
                                elif connection_info.id in connection_info_id_list:
                                    connection_info = connection_info
                                else:
                                    pass
                                    # raise ValueError("sameNameConnectionInfo")
                                created_connection_info_id_list.append(
                                    connection_info.id
                                )

                                create_integration = generate_integration(
                                    integration,
                                    connection_info.id,
                                    created_gateway_api.id,
                                )

                            # Create Integration
                            if integration.connection_info is None:
                                create_integration = generate_integration(
                                    integration, None, created_gateway_api.id
                                )
                            created_integration = await self.integration_service.create(
                                create_integration, tenant_id
                            )
                            created_integration_id_list.append(created_integration.id)

                            if gateway_api.routes:
                                filtered_routes = [
                                    p
                                    for p in gateway_api.routes
                                    if p.integration_id == integration.id
                                ]
                                create_route_tasks = [
                                    self.route_service.create(
                                        generate_route(
                                            route,
                                            created_gateway_api.id,
                                            created_integration.id,
                                        ),
                                        tenant_id,
                                    )
                                    for route in filtered_routes
                                ]
                                created_routes = await asyncio.gather(
                                    *create_route_tasks
                                )
                                created_route_id_list.extend(
                                    [route.id for route in created_routes]
                                )

                            if integration.parameter_mappings:
                                create_parameter_mapping_tasks = [
                                    self.parameter_mapping_service.create(
                                        generate_parameter_mapping(
                                            mapping, created_integration.id
                                        ),
                                        tenant_id,
                                    )
                                    for mapping in integration.parameter_mappings
                                ]
                                created_parameter_mappings = await asyncio.gather(
                                    *create_parameter_mapping_tasks
                                )
                                created_parameter_mapping_id_list.extend(
                                    [
                                        mapping.id
                                        for mapping in created_parameter_mappings
                                    ]
                                )

                    if gateway_api.routes:
                        filtered_notRelationRoute = [
                            p for p in gateway_api.routes if p.integration_id is None
                        ]
                        create_route_tasks = [
                            self.route_service.create(
                                generate_route(route, created_gateway_api.id), tenant_id
                            )
                            for route in filtered_notRelationRoute
                        ]
                        created_routes = await asyncio.gather(*create_route_tasks)
                        created_route_id_list.extend(
                            [route.id for route in created_routes]
                        )

                else:
                    raise ValueError("sameNameManageApiOrGatewayApi")

            except ValueError as Ex:
                await self.rollback(
                    created_api_scope_id_list,
                    created_parameter_mapping_id_list,
                    created_route_id_list,
                    created_integration_id_list,
                    created_gateway_api_id_list,
                    created_connection_info_id_list,
                    tenant_id,
                )
                raise Ex
            except Exception as Ex:
                await self.rollback(
                    created_api_scope_id_list,
                    created_parameter_mapping_id_list,
                    created_route_id_list,
                    created_integration_id_list,
                    created_gateway_api_id_list,
                    created_connection_info_id_list,
                    tenant_id,
                )
                raise Ex

        return importGatewayApis

    async def rollback(
        self,
        api_scope_ids,
        parameter_mapping_ids,
        route_ids,
        integration_ids,
        gateway_api_ids,
        connection_info_ids,
        tenant_id,
    ):
        if api_scope_ids:
            query_args: QueryArgs = QueryArgs(
                where=[Filter(field="id", op=FilterOp.IN, value=api_scope_ids)],
                limit=0,
                offset=0,
            )
            await self.messenger.delete_all_api_scopes(
                query_args.to_serialize(), tenant_id
            )
        if parameter_mapping_ids:
            await self.parameter_mapping_service.delete_by_ids(
                parameter_mapping_ids, tenant_id
            )
        if route_ids:
            await self.route_service.delete_by_ids(route_ids, tenant_id)
        if integration_ids:
            await self.integration_service.delete_by_ids(integration_ids, tenant_id)
        if gateway_api_ids:
            await self.gateway_api_service.delete_by_ids(gateway_api_ids, tenant_id)
        if connection_info_ids:
            await self.connection_info_service.delete_by_ids(
                connection_info_ids, tenant_id
            )


def generate_gateway_api(gateway_api: GatewayApi) -> CreateGatewayApi:
    return CreateGatewayApi(
        name=gateway_api.name,
        path=gateway_api.path,
        identifier=gateway_api.identifier,
        context=gateway_api.context,
        description=gateway_api.description,
        type=gateway_api.type,
    )


def generate_connection_info(connection_info: ConnectionInfo) -> CreateConnectionInfo:
    return CreateConnectionInfo(
        name=connection_info.name,
        description=connection_info.description,
        params=connection_info.params,
        type=connection_info.type,
    )


def generate_integration(
    integration: Integration, connection_info_id: UUID | None, gateway_api_id: UUID
) -> CreateIntegration:
    return CreateIntegration(
        name=integration.name,
        description=integration.description,
        timeout_in_millis=(
            integration.timeout_in_millis if integration.timeout_in_millis else 30000
        ),
        type=integration.type,
        connection=integration.connection,
        gateway_api_id=gateway_api_id,
        connection_info_id=connection_info_id,
        context=integration.context,
        default_route=False,
        default_route_path=None,
        default_route_methods=[],
    )


def generate_route(
    route: Route, gateway_api_id: UUID, integration_id: UUID | None = None
) -> CreateRoute:
    return CreateRoute(
        description=route.description,
        method_type=route.method_type,
        path=route.path,
        scope=route.scope,
        query=route.query,
        cache_timeout=route.cache_timeout,
        rate_limit=route.rate_limit,
        rate_second=route.rate_second,
        retry_count=route.retry_count,
        retry_millisecond=route.retry_millisecond,
        gateway_api_id=gateway_api_id,
        integration_id=integration_id,
    )


def generate_parameter_mapping(
    parameter_mapping: ParameterMapping, integration_id: UUID
) -> CreateParameterMapping:
    return CreateParameterMapping(
        status_code=parameter_mapping.status_code,
        type=parameter_mapping.type,
        param_list=parameter_mapping.param_list,
        integration_id=integration_id,
    )


def generate_manage_api_scope(scope: ApiScope, api_id: UUID) -> CreateApiScope:
    return CreateApiScope(name=scope.name, description=scope.description, api_id=api_id)


def generated_export_gateway_api(
    gateway_api: GatewayApi, scopes: List[Any]
) -> ExportGatewayApi:
    return ExportGatewayApi(
        id=gateway_api.id,
        name=gateway_api.name,
        type=gateway_api.type,
        path=gateway_api.path,
        created_at=gateway_api.created_at,
        description=gateway_api.description,
        integrations=gateway_api.integrations,
        routes=gateway_api.routes,
        identifier=gateway_api.identifier,
        manage_api_id=gateway_api.manage_api_id,
        context=gateway_api.context,
        scopes=scopes,
    )
