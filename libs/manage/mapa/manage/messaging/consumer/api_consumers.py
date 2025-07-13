from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.api.api_model import CreateApi, UpdateApi
from mapa.manage.api.api_service import ApiService
from mapa.core.data.query_args import QueryArgs
from redis.asyncio import Redis


class ApiCreateConsumer(BaseConsumer):
    def __init__(self, api_service: ApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("api.create", "api.create", "mapa-exchange", connection, rredis, wredis)
        self.api_service = api_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        api = CreateApi(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.api_service.create(api, tenant_id)
        return {"id": created.id}


class ApiUpdateConsumer(BaseConsumer):
    def __init__(self, api_service: ApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("api.update", "api.update", "mapa-exchange", connection, rredis, wredis)
        self.api_service = api_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        id = payload["id"]
        api = UpdateApi(**data)
        tenant_id = payload.get("tenant_id")
        updated = await self.api_service.update(id, api, tenant_id)
        return {"id": id}



class ApiDeleteConsumer(BaseConsumer):
    def __init__(self, api_service: ApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("api.delete", "api.delete", "mapa-exchange", connection, rredis, wredis)
        self.api_service = api_service

    async def process_message(self, payload: dict) -> bool:
        api_id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.api_service.delete(api_id, tenant_id)
        return result


class ApiGetConsumer(BaseConsumer):
    def __init__(self, api_service: ApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("api.get", "api.get", "mapa-exchange", connection, rredis, wredis)
        self.api_service = api_service

    async def process_message(self, payload: dict) -> dict:
        api_id = payload["id"]
        tenant_id = payload.get("tenant_id")
        fields = payload.get("fields", [])
        result = await self.api_service.get(api_id, tenant_id, fields)
        if result is None:
            return {}
        return result.model_dump()


class ApiDeleteAllConsumer(BaseConsumer):
    def __init__(self, api_service: ApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("api.delete_all", "api.delete_all", "mapa-exchange", connection, rredis, wredis)
        self.api_service = api_service

    async def process_message(self, payload: dict) -> int:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        deleted_count = await self.api_service.delete_all(QueryArgs(**query_args), tenant_id)
        return deleted_count


class ApiCountConsumer(BaseConsumer):
    def __init__(self, api_service: ApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("api.count", "api.count", "mapa-exchange", connection, rredis, wredis)
        self.api_service = api_service

    async def process_message(self, payload: dict) -> int:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        count = await self.api_service.count(QueryArgs(**query_args), tenant_id)
        return count


class ApiPagingConsumer(BaseConsumer):
    def __init__(self, api_service: ApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("api.paging", "api.paging", "mapa-exchange", connection, rredis, wredis)
        self.api_service = api_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        apis = await self.api_service.paging(QueryArgs(**query_args), tenant_id)
        return apis.model_dump()  # type: ignore


class ApiFindConsumer(BaseConsumer):
    def __init__(self, api_service: ApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("api.find", "api.find", "mapa-exchange", connection, rredis, wredis)
        self.api_service = api_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        apis = await self.api_service.find(QueryArgs(**query_args), tenant_id)
        serialized_apis = [
            api.model_dump() if hasattr(api, "model_dump") else api for api in apis
        ]
        return {"apis": serialized_apis}
