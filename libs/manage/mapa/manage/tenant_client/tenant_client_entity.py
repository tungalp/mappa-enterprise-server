from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from mapa.manage.client.client_entity import ClientEntity

class TenantClientEntity(EntityMixin, TenantMixin, Base):
    """TenantUser Entity"""
    
    __tablename__ = "tenant_client"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    client_id = Column(UUIDType(binary=False), ForeignKey("manage.client.id", ondelete="CASCADE"), nullable=False, index=True)

    client = relationship(ClientEntity, back_populates="tenant_client", cascade="all, delete")