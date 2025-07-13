from sqlalchemy import Column, Text, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from mapa.core.data.base_entity import Base, EntityMixin
from mapa.gateway.integration.integration_entity import IntegrationEntity
from sqlalchemy_utils import UUIDType

class ConnectionInfoEntity(EntityMixin, Base):
    """ConnectionInfoEntity Db Model"""

    __tablename__ = "connection_info"  # type: ignore

    __table_args__ = {'schema': 'gateway'}

    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    params = Column(JSON, nullable=False)
    type = Column(Text, nullable=False)
    
    integration = relationship(IntegrationEntity, back_populates="connection_info")
    
    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, tenant_id, name='connection_info_uk_1')
