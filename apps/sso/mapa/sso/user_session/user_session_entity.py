from sqlalchemy import ARRAY, Boolean, Column, DateTime, func
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from mapa.core.data.base_entity import Base, EntityMixin

class UserSessionEntity(EntityMixin, Base):
    """UserSession Entity"""
    
    __tablename__ = "user_session"
    __table_args__ = {'schema': 'sso'}
    
    user_id = Column(UUIDType(binary=False), nullable=False, index=True)
    authenticated_at = Column(DateTime, nullable=False, default=func.now())
    expired_at = Column(DateTime, nullable=False)
    authenticated = Column(Boolean, nullable=False, default=False)

    user_session_clients = relationship("UserSessionClientEntity", back_populates="user_session", cascade="all, delete, save-update")