from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.api_scope.api_scope_model import CreateApiScope
from mapa.manage.api_scope.api_scope_service import ApiScopeService
from mapa.core.data.query_args import QueryArgs
from redis.asyncio import Redis



class ApiScopeCreateAllConsumer(BaseConsumer):
    def __init__(
        self, api_scope_service: ApiScopeService, connection: RabbitConnection, rredis: Redis, wredis: Redis
    ):
        super().__init__(
            "api_scope.create_all", "api_scope.create_all", "mapa-exchange", connection, rredis, wredis
        )
        self.api_scope_service = api_scope_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        api_scopes = [CreateApiScope(**item) for item in data]
        tenant_id = payload.get("tenant_id")
        result = await self.api_scope_service.create_all(api_scopes, tenant_id)
        return {"created_count": len(result)}


class ApiScopeCreateConsumer(BaseConsumer):
    def __init__(
        self, api_scope_service: ApiScopeService, connection: RabbitConnection, rredis: Redis, wredis: Redis
    ):
        super().__init__(
            "api_scope.create", "api_scope.create", "mapa-exchange", connection, rredis, wredis
        )
        self.api_scope_service = api_scope_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        api_scope = CreateApiScope(**data)
        tenant_id = payload.get("tenant_id")
        result = await self.api_scope_service.create(api_scope, tenant_id)
        return {"id": result.id}


class ApiScopeDeleteAllConsumer(BaseConsumer):
    def __init__(
        self, api_scope_service: ApiScopeService, connection: RabbitConnection, rredis: Redis, wredis: Redis
    ):
        super().__init__(
            "api_scope.delete_all", "api_scope.delete_all", "mapa-exchange", connection, rredis, wredis
        )
        self.api_scope_service = api_scope_service

    async def process_message(self, payload: dict) -> int:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        deleted = await self.api_scope_service.delete_all(
            QueryArgs(**query_args), tenant_id
        )
        return deleted



class ApiScopePagingConsumer(BaseConsumer):
    def __init__(
        self, api_scope_service: ApiScopeService, connection: RabbitConnection, rredis: Redis, wredis: Redis
    ):
        super().__init__(
            "api_scope.paging", "api_scope.paging", "mapa-exchange", connection, rredis, wredis
        )
        self.api_scope_service = api_scope_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        api_scopes = await self.api_scope_service.paging(
            QueryArgs(**query_args), tenant_id
        )
        return api_scopes.model_dump()  # type: ignore


class ApiScopeFindConsumer(BaseConsumer):
    def __init__(
        self, api_scope_service: ApiScopeService, connection: RabbitConnection, rredis: Redis, wredis: Redis
    ):
        super().__init__("api_scope.find", "api_scope.find", "mapa-exchange", connection, rredis, wredis)
        self.api_scope_service = api_scope_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        api_scopes = await self.api_scope_service.find(
            QueryArgs(**query_args), tenant_id
        )
        serialized_api_scopes = [
            api_scope.model_dump() if hasattr(api_scope, "model_dump") else api_scope
            for api_scope in api_scopes
        ]
        return {"api_scopes": serialized_api_scopes}

