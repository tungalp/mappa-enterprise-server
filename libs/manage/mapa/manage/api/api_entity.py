from sqlalchemy import ARRAY, Boolean, Column, Text, Integer, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy.orm import relationship
from mapa.manage.client_api.client_api_entity import ClientApiEntity
from mapa.manage.constants import Algorithms, LevelTypes
from mapa.manage.api_scope.api_scope_entity import ApiScopeEntity
from sqlalchemy_utils import UUIDType


class ApiEntity(EntityMixin,Base):
    """Api Db Model"""

    __tablename__ = "api"  # type: ignore
    __table_args__ = {'schema': 'manage'}

    name = Column(Text, nullable=False)
    identifier = Column(Text, nullable=False)
    allow_offline_access = Column(Boolean, nullable=True, default=False)
    skip_consent_for_verifiable_first_party_clients = Column(
        ARRAY(Text), nullable=True)
    token_lifetime = Column(Integer, nullable=True, default=72000)
    token_lifetime_for_web = Column(Integer, nullable=True, default=72800)
    signing_alg = Column(Text, nullable=True,
                         default=Algorithms.Asymmetric.RS256)
    is_system = Column(Boolean, nullable=True, default=False)
    api_scopes = relationship(
        ApiScopeEntity, back_populates="api", cascade="all, delete-orphan")
    level_type = Column(Text, nullable=True, default=LevelTypes.THIRD_PARTY)

    client_api = relationship(
        ClientApiEntity, back_populates="api", cascade="all, delete-orphan")
    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(identifier, tenant_id,  name='api_uk_1')
