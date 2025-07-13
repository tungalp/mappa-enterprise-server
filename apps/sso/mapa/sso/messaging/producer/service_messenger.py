from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.rabbitmq.enums import OutboxStatus
from mapa.core.rabbitmq.message_bus import MessageBus
from nanoid import generate
import json
import uuid
from aio_pika import Message
from mapa.sso.outbox.outbox_service import OutboxService
from mapa.sso.outbox.outbox_model import CreateOutbox
from sqlalchemy import text


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
                    FROM sso.outbox 
                    WHERE status = :status 
                    ORDER BY created_at 
                    LIMIT :limit 
                    FOR UPDATE SKIP LOCKED
                    """
                ),
                {"status": OutboxStatus.PENDING.value, "limit": limit},
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
                            "UPDATE sso.outbox SET status = :status, processed_at = now() WHERE id = :id"
                        ),
                        {"status": OutboxStatus.PROCESSED.value, "id": outbox_id},
                    )
                except Exception:
                    # retry_count al ve güncelle
                    retry_res = await session.execute(
                        text("SELECT retry_count FROM sso.outbox WHERE id = :id"),
                        {"id": outbox_id}
                    )
                    retry_count = retry_res.scalar_one()
                    new_retry = retry_count + 1
                    new_status = (
                        OutboxStatus.DEAD_LETTERED.value if new_retry >= max_retry else OutboxStatus.FAILED.value
                    )

                    await session.execute(
                        text("""
                            UPDATE sso.outbox
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
            
    async def get_client_by_client_id(
        self, client_id: str, tenant_id: str | None = None
    ):
        return await self.bus.publish_with_response(
            "client.get_client_by_client_id",
            {"client_id": client_id, "tenant_id": tenant_id},
        )

    async def create_user(self, data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response(
            "user.create", {"data": data, "tenant_id": tenant_id}
        )

    async def tenant_count(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response(
            "tenant.count", {"query_args": query_args, "tenant_id": tenant_id}
        )

    async def tenant_create(self, data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response(
            "tenant.create", {"data": data, "tenant_id": tenant_id}
        )

    async def organization_type_create(self, data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response(
            "organization_type.create", {"data": data, "tenant_id": tenant_id}
        )

    async def organization_create(self, data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response(
            "organization.create", {"data": data, "tenant_id": tenant_id}
        )

    async def organization_user_create(self, data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response(
            "organization_user.create", {"data": data, "tenant_id": tenant_id}
        )

    async def tenant_user_create(self, data: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response(
            "tenant_user.create", {"data": data, "tenant_id": tenant_id}
        )

    async def invitation_update(
        self, id: str, data: dict, tenant_id: str | None = None
    ):
        return await self.bus.publish_with_response(
            "invitation.update", {"id": id, "data": data, "tenant_id": tenant_id}
        )

    async def invitation_get(
        self, api_id: str, tenant_id: str | None = None, fields: list[str] = []
    ):
        return await self.bus.publish_with_response(
            "invitation.get", {"id": api_id, "tenant_id": tenant_id, "fields": fields}
        )

    async def check_ldap_connection_with_mail_password(
        self, ldap_server_id: str, email: str, password: str
    ):
        """
        LDAP sunucusuna verilen e-posta ve parola ile bağlanma denemesi yapar.
        Başarılı olursa True, aksi halde False döner.
        """
        return await self.bus.publish_with_response(
            "user.ldap.check_connection",
            {
                "ldap_server_id": ldap_server_id,
                "email": email,
                "password": password,
            },
        )

    async def check_password(self, user_id: str, password: str):
        """
        Kullanıcının mevcut şifresinin doğruluğunu kontrol eder.
        """
        return await self.bus.publish_with_response(
            "user.password_check",
            {
                "user_id": user_id,
                "password": password,
            },
        )

    async def update_password(self, user_id: str, new_password: str):
        """
        Kullanıcının şifresini yeni parola ile günceller.
        """
        return await self.bus.publish_with_response(
            "user.password_update",
            {
                "user_id": user_id,
                "password": new_password,
            },
        )

    async def get_by_user_id(
        self, user_id: str, fields: list[str] = [], tenant_id: str | None = None
    ):
        """
        Belirtilen kullanıcı ID'si ile kullanıcıyı getirir.
        Alan listesi (fields) ve tenant_id opsiyoneldir.
        """
        return await self.bus.publish_with_response(
            "user.get_by_id",
            {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "fields": fields,
            },
        )

    async def user_get_by_email(
        self, email: str, fields: list[str] = [], tenant_id: str | None = None
    ):
        """
        E-posta adresine göre kullanıcıyı getirir.
        Alan listesi (fields) ve tenant_id opsiyoneldir.
        """
        return await self.bus.publish_with_response(
            "user.get_by_email",
            {
                "email": email,
                "tenant_id": tenant_id,
                "fields": fields,
            },
        )

    async def client_get(
        self, id: str, tenant_id: str | None = None, fields: list[str] = []
    ):
        """
        Belirli bir istemciyi ID ile getirir.
        """
        return await self.bus.publish_with_response(
            "client.get", {"id": id, "tenant_id": tenant_id, "fields": fields}
        )

    async def get_user_scopes(
        self, client_id: str, user_id: str, tenant_id: str | None = None
    ):
        return await self.bus.publish_with_response(
            "user.get_user_scopes",
            {"client_id": client_id, "id": user_id, "tenant_id": tenant_id},
        )

    async def client_api_scope_get(
        self, client_id: str, tenant_id: str | None = None, fields: list[str] = []
    ):
        return await self.bus.publish_with_response(
            "client.get_client_scopes",
            {"client_id": client_id, "tenant_id": tenant_id, "fields": fields},
        )

    async def user_find(self, query_args: dict, tenant_id: str | None = None):
        return await self.bus.publish_with_response(
            "user.find", {"query_args": query_args, "tenant_id": tenant_id}
        )

    async def find_by_user_id(self, user_id: str):
        """
        Belirtilen kullanıcı ID'si ile kullanıcıyı getirir.
        Alan listesi (fields) ve tenant_id opsiyoneldir.
        """
        return await self.bus.publish_with_response(
            "tenant_user.find_by_user_id",
            {"id": user_id},
        )

    async def get_client_info(self, client_id: str, tenant_id: str | None = None):
        """
        Belirtilen kullanıcı ID'si ile kullanıcıyı getirir.
        Alan listesi (fields) ve tenant_id opsiyoneldir.
        """
        return await self.bus.publish_with_response(
            "client.get_client_info",
            {"client_id": client_id, "tenant_id": tenant_id},
        )

    async def delete_organization_user(self, client_id: str, tenant_id: str | None = None):
        """Belirtilen ID'ye sahip organizasyon kullanıcısını siler."""
        try:
            await self.publish_event(
                aggregate_type="organization_user",
                aggregate_id=client_id,
                message_type="organization_user.delete",
                payload={"id": client_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    async def delete_organization_type(self, client_id: str, tenant_id: str | None = None):
        """Belirtilen ID'ye sahip organizasyon türünü siler."""
        try:
            await self.publish_event(
                aggregate_type="organization_type",
                aggregate_id=client_id,
                message_type="organization_type.delete",
                payload={"id": client_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    async def delete_organization(self, client_id: str, tenant_id: str | None = None):
        """Belirtilen ID'ye sahip organizasyonu siler."""
        try:
            await self.publish_event(
                aggregate_type="organization",
                aggregate_id=client_id,
                message_type="organization.delete",
                payload={"id": client_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    async def delete_tenant_user(self, client_id: str, tenant_id: str | None = None):
        """Belirtilen ID'ye sahip tenant kullanıcısını siler."""
        try:
            await self.publish_event(
                aggregate_type="tenant_user",
                aggregate_id=client_id,
                message_type="tenant_user.delete",
                payload={"id": client_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    async def delete_tenant(self, client_id: str, tenant_id: str | None = None):
        try:
            await self.publish_event(
                aggregate_type="tenant",
                aggregate_id=client_id,
                message_type="tenant.delete",
                payload={"id": client_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    async def delete_user(self, client_id: str, tenant_id: str | None = None):
        """Belirtilen ID'ye sahip kullanıcıyı siler."""
        try:
            await self.publish_event(
                aggregate_type="user",
                aggregate_id=client_id,
                message_type="user.delete",
                payload={"id": client_id, "tenant_id": tenant_id},
                tenant_id=tenant_id
            )
        except Exception as ex:
            raise RuntimeError("Outbox event yazılamadı") from ex

    async def tenant_client_get_client_id(self, client_id: str):
        """Belirtilen ID'ye sahip tenant istemcisini getirir."""
        return await self.bus.publish_with_response(
            "tenant_client.get_client_id", {"id": client_id}
        )