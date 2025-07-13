from sqlalchemy import Column, Text, UniqueConstraint, JSON, Boolean
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from nanoid import generate
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from mapa.gateway.constant import ApiTypes
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.route.route_entity import RouteEntity

class GatewayApiEntity(EntityMixin, Base):
    """GatewayApi Db Model"""

    __tablename__ = "gateway_api"  # type: ignore

    __table_args__ = {'schema': 'gateway'}

    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Text, nullable=False, default=ApiTypes.HTTP)
    path = Column(Text, nullable=False)
    
    identifier = Column(Text, nullable=False)
    manage_api_id = Column(UUIDType(binary=False), nullable=True, index=True)
    
    context = Column(JSON, nullable=True)
    
    integrations = relationship(IntegrationEntity, back_populates="gateway_api", cascade="all, delete-orphan")
    routes = relationship(RouteEntity, back_populates="gateway_api", cascade="all, delete-orphan")

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, tenant_id, name='gateway_api_uk_1')
    UniqueConstraint(identifier, tenant_id, name='gateway_api_uk_2')
    