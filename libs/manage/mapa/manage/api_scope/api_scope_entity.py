from sqlalchemy import ARRAY, Boolean, Column, Text, ForeignKey, UniqueConstraint, Index
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


class ApiScopeEntity(EntityMixin, TenantMixin, Base):
    """ApiScope Db Model"""

    __tablename__ = "api_scope"  # type: ignore
    __table_args__ = {'schema': 'manage'}

    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    api_id = Column(UUIDType(binary=False), ForeignKey(
        "manage.api.id", ondelete="CASCADE"), nullable=False)
    api = relationship("ApiEntity")

    UniqueConstraint(name, api_id, name='api_scope_uk_1')
