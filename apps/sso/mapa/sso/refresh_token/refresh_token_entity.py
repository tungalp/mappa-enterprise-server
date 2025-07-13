from sqlalchemy import Boolean, Column, DateTime, Text, Integer
from sqlalchemy_utils import UUIDType
from mapa.core.data.base_entity import Base, EntityMixin


class RefreshTokenEntity(EntityMixin, Base):
    """RefreshToken Db Model"""

    __tablename__ = "refresh_token"
    __table_args__ = {'schema': 'sso'}

    user_session_id = Column(UUIDType(binary=False), nullable=False)
    user_id = Column(UUIDType(binary=False), nullable=False)
    client_id = Column(Text, nullable=False)
    audience = Column(Text, nullable=False)
    num_used = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)
    expired_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    last_used_at = Column(DateTime, nullable=True)
    nonce = Column(Text, nullable=True)