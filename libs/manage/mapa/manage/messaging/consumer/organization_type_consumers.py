from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization_type.organization_type_service import OrganizationTypeService
from redis.asyncio import Redis


class OrganizationTypeCreateConsumer(BaseConsumer):
    def __init__(self, organization_type_service: OrganizationTypeService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("organization_type.create", "organization_type.create", "mapa-exchange", connection, rredis, wredis)
        self.service = organization_type_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        org_type = CreateOrganizationType(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.service.create(org_type, tenant_id)
        return {"id": created.id}
    
    
class OrganizationTypeDeleteConsumer(BaseConsumer):
    def __init__(self, organization_type_service: OrganizationTypeService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("organization_type.delete", "organization_type.delete", "mapa-exchange", connection, rredis, wredis)
        self.organization_type_service = organization_type_service

    async def process_message(self, payload: dict) -> bool:
        id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.organization_type_service.delete(id, tenant_id)
        return result