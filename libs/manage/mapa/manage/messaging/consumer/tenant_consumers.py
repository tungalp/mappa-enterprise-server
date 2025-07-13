from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.core.data.query_args import QueryArgs
from mapa.manage.tenant.tenant_model import CreateTenant
from mapa.manage.tenant.tenant_service import TenantService
from redis.asyncio import Redis



class TenantCreateConsumer(BaseConsumer):
    def __init__(self, tenant_service: TenantService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant.create", "tenant.create", "mapa-exchange", connection, rredis, wredis)
        self.tenant_service = tenant_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        tenant = CreateTenant(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.tenant_service.create(tenant, tenant_id)
        return {"id": created.id}
    
    
class TenantFindConsumer(BaseConsumer):
    def __init__(self, tenant_service: TenantService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant.find", "tenant.find", "mapa-exchange", connection, rredis, wredis)
        self.tenant_service = tenant_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        tenants = await self.tenant_service.find(QueryArgs(**query_args), tenant_id)
        serialized_tenants = [
            tenant.model_dump() if hasattr(tenant, "model_dump") else tenant
            for tenant in tenants
        ]
        return {"tenants": serialized_tenants}


class TenantCountConsumer(BaseConsumer):
    def __init__(self, tenant_service: TenantService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant.count", "tenant.count", "mapa-exchange", connection, rredis, wredis)
        self.tenant_service = tenant_service

    async def process_message(self, payload: dict) -> int:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        count = await self.tenant_service.count(QueryArgs(**query_args), tenant_id)
        return count


class TenantPagingConsumer(BaseConsumer):
    def __init__(self, tenant_service: TenantService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant.paging", "tenant.paging", "mapa-exchange", connection, rredis, wredis)
        self.tenant_service = tenant_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        tenants = await self.tenant_service.paging(QueryArgs(**query_args), tenant_id)
        return tenants.model_dump()  # type: ignore


class TenantGetConsumer(BaseConsumer):
    def __init__(self, tenant_service: TenantService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant.get", "tenant.get", "mapa-exchange", connection, rredis, wredis)
        self.tenant_service = tenant_service

    async def process_message(self, payload: dict) -> dict:
        id = payload["id"]
        fields = payload.get("fields", [])
        result = await self.tenant_service.get(id, None, fields)
        if result is None:
            return {}
        return result.model_dump()


class TenantDeleteConsumer(BaseConsumer):
    def __init__(self, tenant_service: TenantService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant.delete", "tenant.delete", "mapa-exchange", connection, rredis, wredis)
        self.tenant_service = tenant_service

    async def process_message(self, payload: dict) -> bool:
        id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.tenant_service.delete(id, tenant_id)
        return result