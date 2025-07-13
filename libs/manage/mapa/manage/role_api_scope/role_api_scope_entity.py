from sqlalchemy import Column, ForeignKey, Integer, Text, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship


class RoleApiScopeEntity(EntityMixin, TenantMixin, Base):
    """RoleApiScope Entity"""
    
    __tablename__ = "role_api_scope"  # type: ignore
    __table_args__ = {'schema': 'manage'}

    role_id = Column(UUIDType(binary=False), ForeignKey("manage.role.id", ondelete="CASCADE"), nullable=False, index=True)
    api_scope_id = Column(UUIDType(binary=False), ForeignKey("manage.api_scope.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = relationship("RoleEntity")
    api_scope = relationship("ApiScopeEntity")
    
    UniqueConstraint(role_id, api_scope_id,
                         name='role_api_scope_uk_1')
    
