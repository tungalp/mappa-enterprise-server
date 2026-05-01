from sqlalchemy import Column, String, ForeignKey, DateTime, func, Uuid, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin

class MessageEntity(EntityMixin, TenantMixin, Base):
    __tablename__ = "message"
    __table_args__ = {"schema": "messaging"}

    sender_id = Column(Uuid(), nullable=False)
    receiver_id = Column(Uuid(), nullable=True) # For DM
    room_id = Column(Uuid(), ForeignKey("messaging.room.id"), nullable=True) # For Group
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False, default="text") # text, image, file, signal
    
    read1_at = Column(DateTime, nullable=True) # For receiver 1
    read2_at = Column(DateTime, nullable=True) # For receiver 2 / group receipts
    
    creator_user_id = Column(Uuid(), nullable=True)
    updater_user_id = Column(Uuid(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())

    files = relationship("MessageFileEntity", back_populates="message", cascade="all, delete-orphan")

class MessageFileEntity(EntityMixin, TenantMixin, Base):
    __tablename__ = "message_files"
    __table_args__ = {"schema": "messaging"}

    message_id = Column(Uuid(), ForeignKey("messaging.message.id"), nullable=False)
    file_url = Column(String, nullable=False)
    data_hash = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)

    message = relationship("MessageEntity", back_populates="files")

class SignalEntity(EntityMixin, TenantMixin, Base):
    """Historical GIS signals (tracks) persistence"""
    __tablename__ = "signal"
    __table_args__ = {"schema": "messaging"}

    entity_id = Column(String, nullable=False, index=True)
    layer = Column(String, nullable=False, index=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    metadata_json = Column(Text, nullable=True) # JSON payload
    timestamp = Column(DateTime, server_default=func.now())
