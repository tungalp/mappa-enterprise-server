from sqlalchemy import ForeignKey, Uuid, Boolean, Column, Text, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import uuid

class OrganizationTypeEntity(EntityMixin, Base):
    """OrganizationType Db Model"""

    __tablename__ = "organization_type"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(UUIDType(binary=False),  nullable=True, index=True)
    is_root = Column(Boolean, nullable=False, default=False)


    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, tenant_id, name='organization_type_uk_1')