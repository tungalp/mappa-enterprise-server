import enum
from sqlalchemy import Column, String, Text, Enum, Integer, DateTime
from sqlalchemy_utils import UUIDType
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin

class OutboxStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    DEAD_LETTERED = "DEAD_LETTERED"

class OutboxEntity(EntityMixin, TenantMixin, Base):
    __tablename__ = "outbox"
    __table_args__ = {"schema": "messaging"}

    aggregate_type = Column(String, nullable=False)
    aggregate_id = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    message_payload = Column(Text, nullable=False)
    status = Column(Enum(OutboxStatus), nullable=False, default=OutboxStatus.PENDING)
    retry_count = Column(Integer, default=0)
    processed_at = Column(DateTime(timezone=True), nullable=True)
