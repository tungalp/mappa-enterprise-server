from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from mapa.manage.user.user_entity import UserEntity

class TenantUserEntity(EntityMixin, TenantMixin, Base):
    """TenantUser Entity"""
    
    __tablename__ = "tenant_user"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    user_id = Column(UUIDType(binary=False), ForeignKey("manage.user.id",  ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Text, nullable=False)
    
    user = relationship(UserEntity)
