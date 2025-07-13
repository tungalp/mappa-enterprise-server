from sqlalchemy import Column, Text, UniqueConstraint, JSON, Boolean, Integer, ForeignKey
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from nanoid import generate
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from mapa.gateway.constant import IntegrationTypes
from mapa.gateway.parameter_mapping.parameter_mapping_entity import ParameterMappingEntity


class IntegrationEntity(EntityMixin, TenantMixin, Base):
    """Integration Db Model"""

    __tablename__ = "integration"  # type: ignore

    __table_args__ = {'schema': 'gateway'}

    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    timeout_in_millis = Column(Integer, nullable=False, default = 30000)
    type = Column(Text, nullable=False)
    connection = Column(JSON, nullable=False)
    connection_info_id = Column(UUIDType(binary=False), ForeignKey("gateway.connection_info.id"), nullable=True, index=True)
    gateway_api_id = Column(UUIDType(binary=False), ForeignKey("gateway.gateway_api.id", ondelete="CASCADE"), nullable=False, index=True)
    
    context = Column(JSON, nullable=True)
    
    connection_info = relationship("ConnectionInfoEntity")
    gateway_api = relationship("GatewayApiEntity",)
    parameter_mappings = relationship(ParameterMappingEntity, back_populates="integration", cascade="all, delete-orphan")
       
    UniqueConstraint(gateway_api_id, name, name='integration_uk_1')