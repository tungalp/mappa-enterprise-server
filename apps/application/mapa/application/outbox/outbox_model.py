from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum

from mapa.core.rabbitmq.enums import OutboxStatus


class Outbox(BaseModel):
    id: UUID
    aggregate_type: str
    aggregate_id: str
    message_type: str
    message_payload: str
    status: OutboxStatus
    retry_count: int = 0
    processed_at: datetime | None = None
    tenant_id: UUID
    created_at: datetime | None = None


class CreateOutbox(BaseModel):
    aggregate_type: str
    aggregate_id: str
    message_type: str
    message_payload: str
    tenant_id: UUID
    status: OutboxStatus


class UpdateOutboxStatus(BaseModel):
    status: OutboxStatus
    retry_count: int | None = None
    processed_at: datetime | None = None


class UpdateAllOutboxStatus(UpdateOutboxStatus):
    pass
