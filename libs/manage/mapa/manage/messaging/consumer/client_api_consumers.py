from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.client_api.client_api_model import CreateClientApi
from mapa.manage.client_api.client_api_service import ClientApiService
from redis.asyncio import Redis


class ClientApiCreateConsumer(BaseConsumer):
    def __init__(
        self, client_api_service: ClientApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis
    ):
        super().__init__(
            "client_api.create", "client_api.create", "mapa-exchange", connection, rredis, wredis
        )
        self.client_api_service = client_api_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        client_api = CreateClientApi(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.client_api_service.create(client_api, tenant_id)
        return {"id": created.id}


class ClientApiDeleteConsumer(BaseConsumer):
    def __init__(
        self, client_api_service: ClientApiService, connection: RabbitConnection, rredis: Redis, wredis: Redis
    ):
        super().__init__(
            "client_api.delete", "client_api.delete", "mapa-exchange", connection, rredis, wredis
        )
        self.client_api_service = client_api_service

    async def process_message(self, payload: dict) -> bool:
        client_api_id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.client_api_service.delete(client_api_id, tenant_id)
        return result
