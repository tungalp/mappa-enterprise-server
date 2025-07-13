from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.organization_user.organization_user_model import CreateOrganizationUser
from mapa.manage.organization_user.organization_user_service import OrganizationUserService
from redis.asyncio import Redis



class OrganizationUserCreateConsumer(BaseConsumer):
    def __init__(self, organization_user_service: OrganizationUserService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("organization_user.create", "organization_user.create", "mapa-exchange", connection, rredis, wredis)
        self.service = organization_user_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        org_user = CreateOrganizationUser(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.service.create(org_user, tenant_id)
        return {"id": created.id}
    
        
class OrganizationUserDeleteConsumer(BaseConsumer):
    def __init__(self, organization_user_service: OrganizationUserService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("organization_user.delete", "organization_user.delete", "mapa-exchange", connection, rredis, wredis)
        self.organization_user_service = organization_user_service

    async def process_message(self, payload: dict) -> bool:
        id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.organization_user_service.delete(id, tenant_id)
        return result