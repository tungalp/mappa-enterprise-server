from sqlalchemy import ARRAY, Boolean, Column, DateTime, Text
from sqlalchemy_utils import UUIDType
from mapa.core.data.base_entity import Base, EntityMixin


class AuthorizationCodeEntity(EntityMixin, Base):
    """AuthorizationCode Db Model"""

    __tablename__ = "authorization_code"  # type: ignore   
    __table_args__ = {'schema': 'sso'}
    
    code = Column(Text, nullable=False, index=True, unique=True)
    user_session_id = Column(UUIDType(binary=False), nullable=False)
    user_id = Column(UUIDType(binary=False), nullable=False)
    client_id = Column(Text, nullable=False)
    scopes = Column(ARRAY(Text), nullable=False)
    redirect_uri = Column(Text, nullable=False)
    audience = Column(Text, nullable=False)
    nonce = Column(Text, nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    code_challenge = Column(Text, nullable=True)
    code_challenge_method = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    expired_at = Column(DateTime, nullable=False)