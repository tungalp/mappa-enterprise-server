from sqlalchemy import ForeignKey, Uuid, Column, Text, DateTime, Boolean, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

class InvitationEntity(EntityMixin, Base):
    """Invitation Db Model"""

    __tablename__ = "invitation"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    email = Column(Text, nullable=False)
    user_id = Column(UUIDType(binary=False),  nullable=False, index=True)
    used = Column(Boolean, nullable=False, default=False)
    expired_at = Column(DateTime, nullable=False)
    
    organization_id = Column(UUIDType(binary=False), ForeignKey("manage.organization.id", ondelete="SET NULL"),nullable=True)
    
    organization = relationship("OrganizationEntity")
    
    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant = Column(UUIDType(binary=False), index=True, nullable=True)
    UniqueConstraint(email, tenant, organization_id,  name='invitation_uk_1')
