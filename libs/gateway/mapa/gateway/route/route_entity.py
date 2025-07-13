import uuid
from sqlalchemy import Column, Text,Integer, UniqueConstraint, JSON, Boolean, ForeignKey
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from nanoid import generate
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from mapa.gateway.constant import MethodTypes


class RouteEntity(EntityMixin, TenantMixin, Base):
    """Route Db Model"""

    __tablename__ = "route"  # type: ignore

    __table_args__ = {"schema": "gateway"}

    description = Column(Text, nullable=True)
    method_type = Column(Text, nullable=False, default=MethodTypes.GET)
    path = Column(Text, nullable=False)
    scope = Column(Text, nullable=True)
    query = Column(Text, nullable=True)
    cache_timeout = Column(Integer, nullable=True)
    rate_limit = Column(Integer, nullable=True)
    rate_second = Column(Integer, nullable=True)
    retry_count = Column(Integer, nullable=True)
    retry_millisecond = Column(Integer, nullable=True)
    
    full_logging = Column(Boolean, nullable=True, default=False)
    
    gateway_api_id = Column(
        UUIDType(binary=False),
        ForeignKey("gateway.gateway_api.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gateway_api = relationship("GatewayApiEntity")

    integration_id = Column(
        UUIDType(binary=False),
        ForeignKey("gateway.integration.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    integration = relationship("IntegrationEntity")

    UniqueConstraint(gateway_api_id, path, method_type, name="route_uk_1")
