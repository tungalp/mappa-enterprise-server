import json
import hashlib

from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.core.data.query_args import QueryArgs
from mapa.manage.tenant.tenant_model import CreateTenant
from mapa.manage.tenant.tenant_service import TenantService
from redis.asyncio import Redis

# ---------------------------------------------------------------------------
# Cache configuration
# ---------------------------------------------------------------------------
# How long (in seconds) a tenant.find result is cached in Redis.
# Tenants are near-static data — 5 minutes is a safe TTL.
_TENANT_CACHE_TTL_SECONDS = 300

def _tenant_find_cache_key(query_args: dict) -> str:
    """Builds a deterministic Redis key from the query_args payload."""
    serialized = json.dumps(query_args, sort_keys=True, default=str)
    digest = hashlib.sha256(serialized.encode()).hexdigest()[:16]
    return f"cache:tenant.find:{digest}"

def _tenant_all_cache_pattern() -> str:
    """Pattern used to delete all tenant.find cache keys on invalidation."""
    return "cache:tenant.find:*"



class TenantCreateConsumer(BaseConsumer):
    def __init__(self, tenant_service: TenantService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant.create", "tenant.create", "mapa-exchange", connection, rredis, wredis)
        self.tenant_service = tenant_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        tenant = CreateTenant(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.tenant_service.create(tenant, tenant_id)

        # Invalidate all tenant.find cache entries so the new tenant is visible.
        await self._invalidate_tenant_find_cache()
        return {"id": created.id}

    async def _invalidate_tenant_find_cache(self):
        """Deletes every cache:tenant.find:* key from Redis."""
        try:
            pattern = _tenant_all_cache_pattern()
            cursor = 0
            while True:
                cursor, keys = await self._write_redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self._write_redis.delete(*keys)
                if cursor == 0:
                    break
            print("[TenantCreateConsumer] Invalidated tenant.find cache.")
        except Exception as exc:
            print(f"[TenantCreateConsumer] Cache invalidation failed (non-fatal): {exc}")


class TenantFindConsumer(BaseConsumer):
    def __init__(self, tenant_service: TenantService, connection: RabbitConnection, rredis: Redis, wredis: Redis):
        super().__init__("tenant.find", "tenant.find", "mapa-exchange", connection, rredis, wredis)
        self.tenant_service = tenant_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")

        # ── Cache-aside: check Redis first ────────────────────────────────────
        cache_key = _tenant_find_cache_key(query_args)
        try:
            cached = await self._read_redis.get(cache_key)
            if cached:
                print(f"[TenantFindConsumer] Cache HIT: {cache_key}")
                return json.loads(cached)
        except Exception as exc:
            # Redis failure is non-fatal — fall through to DB query.
            print(f"[TenantFindConsumer] Redis read error (non-fatal): {exc}")

        # ── Cache MISS: query the database ───────────────────────────────────
        print(f"[TenantFindConsumer] Cache MISS: {cache_key} — querying database.")
        tenants = await self.tenant_service.find(QueryArgs(**query_args), tenant_id)
        serialized_tenants = [
            tenant.model_dump() if hasattr(tenant, "model_dump") else tenant
            for tenant in tenants
        ]
        result = {"tenants": serialized_tenants}

        # ── Store in Redis with TTL ──────────────────────────────────────────
        try:
            await self._write_redis.set(
                cache_key,
                json.dumps(result, default=str),
                ex=_TENANT_CACHE_TTL_SECONDS,
            )
        except Exception as exc:
            print(f"[TenantFindConsumer] Redis write error (non-fatal): {exc}")

        return result


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

        # Invalidate all tenant.find cache entries so the deleted tenant
        # is no longer served from the cache.
        await self._invalidate_tenant_find_cache()
        return result

    async def _invalidate_tenant_find_cache(self):
        """Deletes every cache:tenant.find:* key from Redis."""
        try:
            pattern = _tenant_all_cache_pattern()
            cursor = 0
            while True:
                cursor, keys = await self._write_redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self._write_redis.delete(*keys)
                if cursor == 0:
                    break
            print("[TenantDeleteConsumer] Invalidated tenant.find cache.")
        except Exception as exc:
            print(f"[TenantDeleteConsumer] Cache invalidation failed (non-fatal): {exc}")