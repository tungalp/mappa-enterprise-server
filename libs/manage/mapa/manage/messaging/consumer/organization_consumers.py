from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.organization.organization_service import OrganizationService
from redis.asyncio import Redis


class OrganizationCreateConsumer(BaseConsumer):
    def __init__(self, organization_service: OrganizationService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("organization.create", "organization.create", "mapa-exchange", connection, rredis, wredis)
        self.service = organization_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        org = CreateOrganization(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.service.create(org, tenant_id)
        return {"id": created.id}


class OrganizationDeleteConsumer(BaseConsumer):
    def __init__(self, organization_service: OrganizationService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("organization.delete", "organization.delete", "mapa-exchange", connection, rredis, wredis)
        self.organization_service = organization_service

    async def process_message(self, payload: dict) -> bool:
        id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.organization_service.delete(id, tenant_id)
        return result