from typing import Any, List
from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.gateway.constant import MethodTypes
from mapa.gateway.route.route_model import (
    CreateRoute,
    UpdateAllRoute,
    UpdateRoute,
    Route,
)
from mapa.gateway.route.route_repository import RouteRepository


class RouteService(
    BaseEntityService[RouteRepository, Route, CreateRoute, UpdateRoute, UpdateAllRoute]
):
    """Route Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RouteRepository, Route)

    async def create(self, route: CreateRoute, tenant_id: str | None = None) -> Route:
        """Route Oluşturma."""

        if (
            route.method_type == MethodTypes.PUT
            or route.method_type == MethodTypes.PATCH
            or route.method_type == MethodTypes.DELETE
        ) and route.cache_timeout is not None:
            raise ValueError("cacheTimeoutNotAllow")

        created_route = await super().create(route, tenant_id)
        return created_route

    async def create_all(
        self, routes: List[CreateRoute], tenant_id: str | None = None
    ) -> List[Route]:
        """Routes Oluşturma."""

        for route in routes:
            if (
                route.method_type == MethodTypes.PUT
                or route.method_type == MethodTypes.PATCH
                or route.method_type == MethodTypes.DELETE
            ) and route.cache_timeout is not None:
                raise ValueError("cacheTimeoutNotAllow")

        created_routes = await super().create_all(routes, tenant_id)
        return created_routes

    async def update(
        self, obj_id: Any, input_obj: UpdateRoute, tenant_id: str | None = None
    ) -> Route | None:
        """Verilen modeli günceller"""

        if (
            input_obj.method_type == MethodTypes.PUT
            or input_obj.method_type == MethodTypes.PATCH
            or input_obj.method_type == MethodTypes.DELETE
        ) and input_obj.cache_timeout is not None:
            raise ValueError("cacheTimeoutNotAllow")

        return await super().update(obj_id, input_obj, tenant_id)

    async def update_by_ids(
        self,
        obj_ids: List[Any],
        input_obj: UpdateRoute,
        tenant_id: str | None = None,
    ) -> bool:
        """Verilen modeli günceller"""

        if (
            input_obj.method_type == MethodTypes.PUT
            or input_obj.method_type == MethodTypes.PATCH
            or input_obj.method_type == MethodTypes.DELETE
        ) and input_obj.cache_timeout is not None:
            raise ValueError("cacheTimeoutNotAllow")

        return await super().update_by_ids(obj_ids, input_obj, tenant_id)

    async def update_all(
        self,
        queryArgs: QueryArgs,
        input_obj: UpdateAllRoute,
        tenant_id: str | None = None,
    ) -> int:
        """Verilen modeli günceller"""

        if (
            input_obj.method_type == MethodTypes.PUT
            or input_obj.method_type == MethodTypes.PATCH
            or input_obj.method_type == MethodTypes.DELETE
        ) and input_obj.cache_timeout is not None:
            raise ValueError("cacheTimeoutNotAllow")

        return await super().update_all(queryArgs, input_obj, tenant_id)
