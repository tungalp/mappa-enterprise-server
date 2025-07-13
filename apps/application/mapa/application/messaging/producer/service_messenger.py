from uuid import UUID
from mapa.application.constants import ApplicationTypes
from mapa.application.content_page.content_page_model import CreateContentPage
from nanoid import generate
import json
from mapa.application.models import CreateClient, CreateApi, CreateApiScope, CreateClientApi
from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.rabbitmq.enums import OutboxStatus
from mapa.core.rabbitmq.message_bus import MessageBus
import json
from mapa.application.outbox.outbox_service import OutboxService
from mapa.application.outbox.outbox_model import CreateOutbox
from sqlalchemy import text
from uuid import uuid4


def generate_client() -> CreateClient:
    return CreateClient(
        name="",
        client_id=generate(
            size=32),
        client_secret=generate(size=64),
        grant_types=['authorization_code', 'refresh_token', 'hybrid'],
        application_type=ApplicationTypes.WEB) 


def generate_api() -> CreateApi:
    return CreateApi(name="", identifier="")


def generate_api_scope(name: str, description: str, api_id: UUID) -> CreateApiScope:
    return CreateApiScope(name=name, description=description, api_id=api_id)


def generate_client_api(client_id: UUID, api_id: UUID) -> CreateClientApi:
    return CreateClientApi(client_id=client_id, api_id=api_id)


def generate_content_page(app_id: UUID) -> CreateContentPage:
    return CreateContentPage(name="", title="", app_id=app_id)


class ServiceMessenger:
    def __init__(self, message_bus: MessageBus, outbox_service: OutboxService, async_db: AsyncDatabase):
        self.bus = message_bus
        self.outbox_service = outbox_service
        self.async_db = async_db

    async def publish_pending_events(self, limit: int = 10, max_retry: int = 5):
        async with self.async_db.session() as session:
            result = await session.execute(
                text(
                    """
                    SELECT id, message_type, message_payload 
                    FROM application.outbox 
                    WHERE status = :status 
                    ORDER BY created_at 
                    LIMIT :limit 
                    FOR UPDATE SKIP LOCKED 
                    """
                ),
                {"status": OutboxStatus.PENDING.value, "limit": limit}, # FOR UPDATE SKIP LOCKED - Reader election'ı sağlıyor
            )
            rows = result.fetchall()

            for row in rows:
                outbox_id, message_type, payload = row
                try:
                    await self.bus.publish_without_response(
                        message_type, json.loads(payload)
                    )
                    await session.execute(
                        text(
                            "UPDATE application.outbox SET status = :status, processed_at = now() WHERE id = :id"
                        ),
                        {"status": OutboxStatus.PROCESSED.value, "id": outbox_id},
                    )
                except Exception:
                    # retry_count al ve güncelle
                    retry_res = await session.execute(
                        text("SELECT retry_count FROM application.outbox WHERE id = :id"),
                        {"id": outbox_id}
                    )
                    retry_count = retry_res.scalar_one()
                    new_retry = retry_count + 1
                    new_status = (
                        OutboxStatus.DEAD_LETTERED.value if new_retry >= max_retry else OutboxStatus.FAILED.value
                    )

                    await session.execute(
                        text("""
                            UPDATE application.outbox
                            SET 
                                retry_count = :retry_count,
                                status = :status
                            WHERE id = :id
                        """),
                        {
                            "retry_count": new_retry,
                            "status": new_status,
                            "id": outbox_id,
                        },
                    )
            await session.commit()
            
    async def publish_event(self, aggregate_type: str, aggregate_id: str, message_type: str, payload: dict, tenant_id):
        try:
            outbox = CreateOutbox(
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                message_type=message_type,
                message_payload=json.dumps(payload, default=str, ensure_ascii=False),
                status=OutboxStatus.PENDING,
                tenant_id=tenant_id
            )
            await self.outbox_service.create(outbox)
        except Exception:
            raise
        
    # **ClientCreateConsumer** için
    async def create_client(self, data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("client.create", {"data": data, "tenant_id": tenant_id})

    # **ClientUpdateConsumer** için
    async def update_client(self, client_id:str, data: dict,  tenant_id: str | None = None):
        return await self.bus.publish_with_response("client.update", {"id":client_id, "data": data, "tenant_id": tenant_id})
    
    # **ApiCreateConsumer** için
    async def create_api(self, data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("api.create", {"data": data, "tenant_id": tenant_id})
    
    # **ApiUpdateConsumer** için
    async def update_api(self,api_id:str,  data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("api.update", {"id":api_id, "data": data, "tenant_id": tenant_id})

    # **ClientApiCreateConsumer** için
    async def create_client_api(self, data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("client_api.create", {"data": data, "tenant_id": tenant_id})

    # **ApiScopeCreateAllConsumer** için
    async def create_api_scopes(self, data: list[dict], tenant_id: str | None = None):
        try:
            aggregate_id = str(uuid4())  # Event ID olarak kullanılabilir
            await self.publish_event(
                aggregate_type="ApiScope",
                aggregate_id=aggregate_id,
                message_type="api_scope.create_all",
                payload={"data": data, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    # **ApiScopeCreateConsumer** için
    async def create_api_scope(self, data: dict, tenant_id: str | None = None):
        try:
            aggregate_id = str(uuid4())  # Event ID olarak kullanılabilir
            await self.publish_event(
                aggregate_type="ApiScope",
                aggregate_id=aggregate_id,
                message_type="api_scope.create",
                payload={"data": data, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex
        
    # ClientApi silme
    async def delete_client_api(self, client_api_id: str, tenant_id: str | None = None):
        try:
            await self.publish_event(
                aggregate_type="client_api",
                aggregate_id=client_api_id,
                message_type="client_api.delete",
                payload={"id": client_api_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    # Api silme
    async def delete_api(self, api_id: str, tenant_id: str | None = None):
        try:
            await self.publish_event(
                aggregate_type="api",
                aggregate_id=api_id,
                message_type="api.delete",
                payload={"id": api_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    # Client silme
    async def delete_client(self, client_id: str, tenant_id: str | None = None):
        try:
            await self.publish_event(
                aggregate_type="client",
                aggregate_id=client_id,
                message_type="client.delete",
                payload={"id": client_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    # **ClientGetByClientIdConsumer** için
    async def get_client_by_client_id(self, client_id: str, tenant_id: str | None = None):
        return await self.bus.publish_with_response("client.get_client_by_client_id", {"client_id": client_id, "tenant_id": tenant_id})

    # **ApiGetConsumer** için
    async def get_api(self, api_id: str, tenant_id: str | None = None, fields: list[str] = []):
        return await self.bus.publish_with_response("api.get", {
            "id": api_id,
            "tenant_id": tenant_id,
            "fields": fields
        })

    # Client toplu silme
    async def delete_all_clients(self, query_args: dict, tenant_id: str | None = None):
        try:
            await self.publish_event(
                aggregate_type="client",
                aggregate_id="bulk",
                message_type="client.delete_all",
                payload={"query_args": query_args, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    # Api toplu silme
    async def delete_all_apis(self, query_args: dict, tenant_id: str | None = None):
        try:
            await self.publish_event(
                aggregate_type="api",
                aggregate_id="bulk",
                message_type="api.delete_all",
                payload={"query_args": query_args, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    # ApiScope toplu silme
    async def delete_all_api_scopes(self, query_args: dict, tenant_id: str | None = None):
        try:
            await self.publish_event(
                aggregate_type="api_scope",
                aggregate_id="bulk",
                message_type="api_scope.delete_all",
                payload={"query_args": query_args, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex
        
    # **ApiFindConsumer** için
    async def api_find(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("api.find", {"query_args": query_args, "tenant_id": tenant_id})

    # **ApiScopeFindConsumer** için
    async def api_scope_find(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("api_scope.find", {"query_args": query_args, "tenant_id": tenant_id})

    # **ClientFindConsumer** için
    async def client_find(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("client.find", {"query_args": query_args, "tenant_id": tenant_id})

    # **ApiPagingConsumer** için
    async def api_paging(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("api.paging", {"query_args": query_args, "tenant_id": tenant_id})
    
    # **ApiCountConsumer** için
    async def api_count(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("api.count", {"query_args": query_args, "tenant_id": tenant_id})

    # **ClientPagingConsumer** için
    async def client_paging(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("client.paging", {"query_args": query_args, "tenant_id": tenant_id})

    # **TenantFindConsumer** için
    async def tenant_find(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("tenant.find", {"query_args": query_args, "tenant_id": tenant_id})

    # **TenantPagingConsumer** için
    async def tenant_paging(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response("tenant.paging", {"query_args": query_args, "tenant_id": tenant_id})

    # **TenantGetConsumer** için
    async def tenant_get(self, tenant_id: str, fields: list[str] = []):
        return await self.bus.publish_with_response("tenant.get", {"id": tenant_id, "fields": fields})