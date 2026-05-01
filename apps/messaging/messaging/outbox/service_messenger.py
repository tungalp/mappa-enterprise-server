import json
from uuid import UUID, uuid4
from sqlalchemy import text
from mapa.core.data.async_db import AsyncDatabase
from messaging.outbox.outbox_entity import OutboxStatus
from messaging.outbox.service import OutboxService
from messaging.outbox.model import CreateOutbox
from mapa.core.rabbitmq.message_bus import MessageBus

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
                    FROM messaging.outbox 
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
                            "UPDATE messaging.outbox SET status = :status, processed_at = now() WHERE id = :id"
                        ),
                        {"status": OutboxStatus.PROCESSED.value, "id": outbox_id},
                    )
                except Exception:
                    retry_res = await session.execute(
                        text("SELECT retry_count FROM messaging.outbox WHERE id = :id"),
                        {"id": outbox_id}
                    )
                    retry_count = retry_res.scalar_one()
                    new_retry = retry_count + 1
                    new_status = (
                        OutboxStatus.DEAD_LETTERED.value if new_retry >= max_retry else OutboxStatus.FAILED.value
                    )

                    await session.execute(
                        text("""
                            UPDATE messaging.outbox
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
