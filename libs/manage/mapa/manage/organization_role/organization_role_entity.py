from sqlalchemy import Column, Text, DateTime, ForeignKey, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship

class OrganizationRoleEntity(EntityMixin, TenantMixin, Base):
    """OrganizationRole Db Model"""

    __tablename__ = "organization_role"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    organization_id = Column(UUIDType(binary=False), ForeignKey("manage.organization.id", ondelete="CASCADE" ),  nullable=False, index=True)
    role_id = Column(UUIDType(binary=False), ForeignKey("manage.role.id", ondelete="CASCADE"),  nullable=False, index=True)

    role = relationship("RoleEntity")
    organization = relationship("OrganizationEntity")
    
    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=True)
    UniqueConstraint(role_id, organization_id, tenant_id,  name='organization_role_uk_1')