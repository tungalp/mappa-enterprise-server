from sqlalchemy import Column, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship

class OrganizationClientEntity(EntityMixin, TenantMixin, Base):
    """OrganizationClient Db Model"""

    __tablename__ = "organization_client"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    organization_id = Column(UUIDType(binary=False), ForeignKey("manage.organization.id", ondelete="CASCADE" ),  nullable=False, index=True)
    client_id = Column(Text, ForeignKey("manage.client.client_id", ondelete="CASCADE"),  nullable=False, index=True)

    client = relationship("ClientEntity")
    organization = relationship("OrganizationEntity")
    is_hierarchical = Column(Boolean, nullable=False, default=False)
    
    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=True)
    UniqueConstraint(client_id, organization_id, tenant_id,  name='organization_client_uk_1')