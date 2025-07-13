from sqlalchemy import ARRAY, Boolean, Column, DateTime, Index, Text
from sqlalchemy_utils import UUIDType
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin


class ConsentEntity(EntityMixin, Base):
    """Consent Db Model"""

    __tablename__ = "consent"
    __table_args__ = (
        Index(f"{__tablename__}_client_id_user_id", "client_id", "user_id"),
        {'schema': 'sso'}
    )
    
    client_id = Column(UUIDType(binary=False), nullable=False)
    user_id = Column(UUIDType(binary=False), nullable=False)
    scopes = Column(ARRAY(Text), nullable=False)
    accepted = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, nullable=True)
