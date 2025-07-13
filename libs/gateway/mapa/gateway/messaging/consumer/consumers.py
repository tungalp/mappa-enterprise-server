from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.gateway.route.route_service import RouteService
from mapa.core.data.query_args import QueryArgs
from redis.asyncio import Redis

class RouteFindConsumer(BaseConsumer):
    def __init__(self, route_service: RouteService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("route.find", "route.find", "mapa-exchange", connection, rredis, wredis)
        self.route_service = route_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        routes = await self.route_service.find(QueryArgs(**query_args), tenant_id)
        serialized_routes = [
            route.model_dump() if hasattr(route, "model_dump") else route
            for route in routes
        ]
        return {"routes": serialized_routes}


class RoutePagingConsumer(BaseConsumer):
    def __init__(self, route_service: RouteService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("route.paging", "route.paging", "mapa-exchange", connection, rredis, wredis)
        self.route_service = route_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        routes = await self.route_service.paging(QueryArgs(**query_args), tenant_id)
        return routes.model_dump()  # type: ignore


class RouteGetConsumer(BaseConsumer):
    def __init__(self, route_service: RouteService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("route.get", "route.get", "mapa-exchange", connection, rredis, wredis)
        self.route_service = route_service

    async def process_message(self, payload: dict) -> dict:
        id = payload["id"]
        fields = payload.get("fields", [])
        result = await self.route_service.get(id, None, fields)
        return result.model_dump()
