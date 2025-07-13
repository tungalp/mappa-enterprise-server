from sqlalchemy import ARRAY, Boolean, Column, Text, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from mapa.manage.client_api.client_api_entity import ClientApiEntity
from mapa.manage.constants import ApplicationTypes, GrantTypes, LevelTypes
from sqlalchemy.orm import relationship
from mapa.manage.organization_client.organization_client_entity import OrganizationClientEntity

class ClientEntity(EntityMixin, Base):
    """Client Db Model"""

    __tablename__ = "client"  # type: ignore
    __table_args__ = {'schema': 'manage'}

    name = Column(Text, nullable=False)
    client_id = Column(Text, nullable=False, index=True)
    client_secret = Column(Text, nullable=False)
    grant_types = Column(ARRAY(Text), nullable=False, default=[GrantTypes.CLIENT_CREDENTIALS, GrantTypes.AUTHORIZATION_CODE, GrantTypes.REFRESH_TOKEN])
    redirect_uris = Column(ARRAY(Text), nullable=True)
    logout_uris = Column(ARRAY(Text), nullable=True)
    client_uri = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    application_type = Column(Text, nullable=False,default=ApplicationTypes.WEB)
    logo_url = Column(Text, nullable=True)
    token_endpoint_auth_method = Column(Text, nullable=True)
    web_origins = Column(ARRAY(Text), nullable=True)
    cors_origins = Column(ARRAY(Text), nullable=True)
    require_consent = Column(Boolean, nullable=True, default=True)
    is_system = Column(Boolean, nullable=True, default=False)
    require_pkce = Column(Boolean, nullable=True, default=False)
    level_type = Column(Text, nullable=True, default=LevelTypes.THIRD_PARTY)

    client_api = relationship(ClientApiEntity, back_populates="client", cascade="all, delete-orphan")
    tenant_client = relationship('TenantClientEntity', back_populates="client", cascade="all, delete-orphan")

    organizations = relationship("OrganizationEntity",secondary="manage.organization_client",
                         foreign_keys=[OrganizationClientEntity.organization_id, OrganizationClientEntity.client_id],back_populates="clients",cascade="all, delete" )

    UniqueConstraint(client_id, name='client_uk_1')
    UniqueConstraint(client_secret, name='client_uk_2')
