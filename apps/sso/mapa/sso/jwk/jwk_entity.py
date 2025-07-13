from sqlalchemy import ARRAY, JSON, Boolean, Column, DateTime, Text, func
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from mapa.core.data.base_entity import Base, EntityMixin

class JwkEntity(EntityMixin, Base):
    """JWK Entity"""
    
    __tablename__ = "jwk"
    __table_args__ = {'schema': 'sso'}
    
    key_id = Column(Text, nullable=False, index=True)
    private_pem = Column(Text, nullable=False)
    public_pem = Column(Text, nullable=False)
    jwk = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    expired_at = Column(DateTime, nullable=False)
