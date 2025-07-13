from sqlalchemy import Column, Text, DateTime, ForeignKey, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship

class RoleUserEntity(EntityMixin, TenantMixin, Base):
    """RoleUser Db Model"""

    __tablename__ = "role_user"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    expired_at = Column(DateTime, nullable=False)
    user_id = Column(UUIDType(binary=False), ForeignKey("manage.user.id", ondelete="CASCADE" ),  nullable=False, index=True)
    role_id = Column(UUIDType(binary=False), ForeignKey("manage.role.id", ondelete="CASCADE"),  nullable=False, index=True)

    role = relationship("RoleEntity")
    user = relationship("UserEntity")
    UniqueConstraint(user_id, role_id,
                         name='role_user_uk_1')
