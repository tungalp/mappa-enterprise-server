from sqlalchemy import ARRAY, Boolean, Column, Text, ForeignKey
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


class ClientApiScopeEntity(EntityMixin, TenantMixin, Base):
    """ClientApiScope Db Model"""

    __tablename__ = "client_api_scope"  # type: ignore
    __table_args__ = {'schema': 'manage'}

    api_scope_id = Column(UUIDType(binary=False), ForeignKey("manage.api_scope.id", ondelete="CASCADE"), nullable=False, index=True)
    client_api_id = Column(UUIDType(binary=False), ForeignKey("manage.client_api.id", ondelete="CASCADE"), nullable=False, index=True)
