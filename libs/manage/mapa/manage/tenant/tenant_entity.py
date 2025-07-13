from sqlalchemy import Column, ForeignKey, Integer, Text, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship

from mapa.manage.user.user_entity import UserEntity


class TenantEntity(EntityMixin, Base):
    """Tenant Entity"""
    
    __tablename__ = "tenant"  # type: ignore
    __table_args__ = {'schema': 'manage'}

    name = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    session_timeout = Column(Integer, nullable=False, default=10080)
    
    user_id = Column(UUIDType(binary=False), ForeignKey("manage.user.id",  ondelete="CASCADE"), nullable=False)
    user = relationship(UserEntity, back_populates="tenant")
    
    UniqueConstraint(name, name='tenant_uk_1')
    