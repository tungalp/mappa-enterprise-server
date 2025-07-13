from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.core.data.query_args import QueryArgs
from mapa.manage.tenant_user.tenant_user_model import CreateTenantUser, TenantUser
from mapa.manage.tenant_user.tenant_user_service import TenantUserService
from redis.asyncio import Redis


class TenantUserFindByUserIdConsumer(BaseConsumer):
    def __init__(self, tenant_user_service: TenantUserService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant_user.find_by_user_id", "tenant_user.find_by_user_id", "mapa-exchange", connection, rredis, wredis)
        self.tenant_user_service = tenant_user_service

    async def process_message(self, payload: dict) -> list:
        id = payload["id"]
        fields = payload.get("fields", [])
        result = await self.tenant_user_service.find_by_user_id(id)
        if result is None:
            return []
        return [tenantuser.model_dump() for tenantuser in result]


class TenantUserCreateConsumer(BaseConsumer):
    def __init__(self, tenant_user_service: TenantUserService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant_user.create", "tenant_user.create", "mapa-exchange", connection, rredis, wredis)
        self.tenant_user_service = tenant_user_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        tenant_user = CreateTenantUser(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.tenant_user_service.create(tenant_user, tenant_id)
        return {"id": created.id, "tenant_id": created.tenant_id, "user_id": created.user_id}
    
    
class TenantUserDeleteConsumer(BaseConsumer):
    def __init__(self, tenant_user_service: TenantUserService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant_user.delete", "tenant_user.delete", "mapa-exchange", connection, rredis, wredis)
        self.tenant_user_service = tenant_user_service

    async def process_message(self, payload: dict) -> bool:
        id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.tenant_user_service.delete(id, tenant_id)
        return result