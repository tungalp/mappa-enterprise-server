from mapa.core.data import BaseRepository
from messaging.outbox.outbox_entity import OutboxEntity

class OutboxRepository(BaseRepository[OutboxEntity]):
    def __init__(self, session_factory):
        super().__init__(session_factory, OutboxEntity)
