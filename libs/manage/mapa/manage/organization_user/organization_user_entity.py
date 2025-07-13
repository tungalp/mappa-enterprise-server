from sqlalchemy import ForeignKey, Uuid, Boolean, Column, Text, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import uuid

class OrganizationUserEntity(EntityMixin, Base):
    """OrganizationUser Db Model"""

    __tablename__ = "organization_user"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    user_id = Column(UUIDType(binary=False), ForeignKey("manage.user.id", ondelete="CASCADE" ),  nullable=False, index=True)
    organization_id = Column(UUIDType(binary=False), ForeignKey("manage.organization.id", ondelete="CASCADE"),  nullable=False, index=True)

    organization = relationship("OrganizationEntity")
    user = relationship("UserEntity")
    
    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=True)
    UniqueConstraint(user_id, organization_id, tenant_id,  name='organization_user_uk_1')