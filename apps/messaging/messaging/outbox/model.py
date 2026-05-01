from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from messaging.outbox.outbox_entity import OutboxStatus

class OutboxBase(BaseModel):
    aggregate_type: str
    aggregate_id: str
    message_type: str
    message_payload: str
    tenant_id: Optional[UUID] = None

class CreateOutbox(OutboxBase):
    status: OutboxStatus = OutboxStatus.PENDING

class Outbox(OutboxBase):
    id: UUID
    status: OutboxStatus
    retry_count: int
    processed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UpdateOutboxStatus(BaseModel):
    id: UUID
    status: OutboxStatus

class UpdateAllOutboxStatus(BaseModel):
    ids: list[UUID]
    status: OutboxStatus
