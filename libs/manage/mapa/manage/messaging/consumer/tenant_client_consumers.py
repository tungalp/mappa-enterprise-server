from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.tenant_client.tenant_client_service import TenantClientService
from redis.asyncio import Redis


class TenantClientGetConsumer(BaseConsumer):
    def __init__(self, tenant_client_service: TenantClientService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant_client.get_client_id", "tenant_client.get_client_id", "mapa-exchange", connection, rredis, wredis)
        self.tenant_client_service = tenant_client_service

    async def process_message(self, payload: dict) -> dict:
        id = payload["id"]
        result = await self.tenant_client_service.find_by_client_id(id)
        if result is None:
            return {}
        return result.model_dump()