from sqlalchemy import ARRAY, Boolean, Column, UniqueConstraint, ForeignKey
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from mapa.manage.api_scope.api_scope_entity import ApiScopeEntity
from mapa.manage.client_api_scope.client_api_scope_entity import ClientApiScopeEntity


class ClientApiEntity(EntityMixin, TenantMixin, Base):
    """ClientApi Db Model"""

    __tablename__ = "client_api"  # type: ignore
    __table_args__ = {'schema': 'manage'}

    api_id = Column(UUIDType(binary=False), ForeignKey("manage.api.id", ondelete="CASCADE"), nullable=False, index=True)
    api = relationship("ApiEntity", back_populates="client_api", cascade="all, delete")
    client_id = Column(UUIDType(binary=False), ForeignKey("manage.client.id", ondelete="CASCADE"), nullable=False, index=True)
    client = relationship("ClientEntity", back_populates="client_api", cascade="all, delete")

    api_scopes = relationship(ApiScopeEntity, secondary="manage.client_api_scope",foreign_keys=[ClientApiScopeEntity.client_api_id, ClientApiScopeEntity.api_scope_id], backref="client_api")

    UniqueConstraint(api_id, client_id,
                     name='client_api_uk_1')
