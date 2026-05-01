from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from messaging.outbox.outbox_entity import OutboxEntity
from messaging.outbox.repository import OutboxRepository
from messaging.outbox.model import Outbox, CreateOutbox, UpdateOutboxStatus, UpdateAllOutboxStatus

class OutboxService(
    BaseEntityService[
        OutboxRepository,
        Outbox,
        CreateOutbox,
        UpdateOutboxStatus,
        UpdateAllOutboxStatus,
    ]
):
    def __init__(self, async_db: AsyncDatabase) -> None:
        self.async_db = async_db
        super().__init__(async_db, OutboxRepository, Outbox)
