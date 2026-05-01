from sqlalchemy import Column, String, ForeignKey, DateTime, func, Uuid
from sqlalchemy.orm import relationship
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin

class RoomEntity(EntityMixin, TenantMixin, Base):
    __tablename__ = "room"
    __table_args__ = {"schema": "messaging"}

    name = Column(String, nullable=False)
    foto = Column(String, nullable=True) # URL to photo
    creator_user_id = Column(Uuid(), nullable=True)
    updater_user_id = Column(Uuid(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())

    users = relationship("RoomUserEntity", back_populates="room", cascade="all, delete-orphan")

class RoomUserEntity(Base):
    __tablename__ = "room_users"
    __table_args__ = {"schema": "messaging"}

    id = Column(Uuid(), primary_key=True, server_default=func.gen_random_uuid())
    room_id = Column(Uuid(), ForeignKey("messaging.room.id"), nullable=False)
    user_id = Column(Uuid(), nullable=False)
    tenant_id = Column(Uuid(), index=True, nullable=True) # TenantMixin manually to control schema
    joined_at = Column(DateTime, server_default=func.now())

    room = relationship("RoomEntity", back_populates="users")
