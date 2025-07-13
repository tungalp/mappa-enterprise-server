import json
from sqlalchemy import text
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.outbox.outbox_model import (
    Outbox,
    CreateOutbox,
    UpdateOutboxStatus,
    UpdateAllOutboxStatus,
)
from mapa.spatial.outbox.outbox_repository import OutboxRepository
from mapa.core.rabbitmq.enums import OutboxStatus


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
