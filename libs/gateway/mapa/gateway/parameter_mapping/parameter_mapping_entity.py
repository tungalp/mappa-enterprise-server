from sqlalchemy import Column, Text, UniqueConstraint, JSON, Integer, ForeignKey, JSON
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from mapa.gateway.constant import ParameterMappingTypes


class ParameterMappingEntity(EntityMixin, TenantMixin, Base):
    """ParameterMapping Db Model"""

    __tablename__ = "parameter_mapping"  # type: ignore

    __table_args__ = {'schema': 'gateway'}

    status_code = Column(Integer, nullable=False, default=0)
    type = Column(Text, nullable=False, default=ParameterMappingTypes.REQUEST)   
    param_list = Column(JSON, nullable=False)
    integration_id = Column(UUIDType(binary=False), ForeignKey("gateway.integration.id", ondelete="CASCADE"), nullable=True, index=True)
    integration = relationship("IntegrationEntity")

    UniqueConstraint(integration_id,type,status_code, name='parameter_mapping_uk_1')
    