from sqlalchemy import Column, Text, UniqueConstraint, JSON, Numeric
from mapa.core.data.base_entity import Base, EntityMixin
from nanoid import generate
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, func
from sqlalchemy.ext.declarative import declarative_base
from mapa.core.rabbitmq.enums import OutboxStatus


class OutboxEntity(EntityMixin, Base):
    """Outbox Db Model"""

    __tablename__ = "outbox"  # type: ignore

    __table_args__ = {"schema": "application"}

    aggregate_type = Column(String, nullable=False)
    aggregate_id = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    message_payload = Column(Text, nullable=False)
    status = Column(
        SQLEnum(OutboxStatus, name="outbox_status_enum_application"),
        nullable=False,
        default=OutboxStatus.PENDING,
    )
    retry_count = Column(Integer, default=0)
    processed_at = Column(DateTime(timezone=True))

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
