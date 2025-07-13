from sqlalchemy import ARRAY, Boolean, Column, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from mapa.core.data.base_entity import Base, EntityMixin

class UserSessionClientEntity(EntityMixin, Base):
    """UserSessionClient Entity"""
    
    __tablename__ = "user_session_client"
    __table_args__ = {'schema': 'sso'}
    
    user_session_id = Column(UUIDType(binary=False), ForeignKey("sso.user_session.id", ondelete="cascade"), nullable=False, index=True)
    client_id = Column(UUIDType(binary=False), nullable=False, index=True)
    tenant = Column(UUIDType(binary=False), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    user_session = relationship("UserSessionEntity", back_populates="user_session_clients")