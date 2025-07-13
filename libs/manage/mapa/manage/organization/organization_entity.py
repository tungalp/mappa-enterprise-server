from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Uuid,
    Boolean,
    Column,
    Text,
    UniqueConstraint,
)
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from mapa.manage.organization_role.organization_role_entity import OrganizationRoleEntity
from mapa.manage.organization_user.organization_user_entity import OrganizationUserEntity
from mapa.manage.organization_client.organization_client_entity import (
    OrganizationClientEntity,
)
import uuid
from sqlalchemy.sql import func
import uuid


# Not : is_hierarchical role bilgilerinin hiyerarşik olarak alıp alınmayacağı bilgisini tutar.
# Bir organization is_hierarchical - > true ise altındaki organizationların da role bilgilerini alacağı anlamına gelir (04.02.2024)
class OrganizationEntity(EntityMixin, Base):
    """Organization Db Model"""

    __tablename__ = "organization"  # type: ignore
    __table_args__ = {"schema": "manage"}

    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(UUIDType(binary=False), nullable=True, index=True)
    is_root = Column(Boolean, nullable=False, default=False)
    is_hierarchical = Column(Boolean, nullable=True)
    geo = Column(JSON, nullable=True)

    integration_id = Column(Text, nullable=True)

    organization_type_id = Column(
        UUIDType(binary=False),
        ForeignKey("manage.organization_type.id"),
        nullable=False,
    )
    organization_type = relationship("OrganizationTypeEntity")

    users = relationship(
        "UserEntity",
        secondary="manage.organization_user",
        foreign_keys=[
            OrganizationUserEntity.user_id,
            OrganizationUserEntity.organization_id,
        ],
        back_populates="organizations",
        cascade="all, delete",
        overlaps="organizations",
    )

    roles = relationship(
        "RoleEntity",
        secondary="manage.organization_role",
        foreign_keys=[
            OrganizationRoleEntity.role_id,
            OrganizationRoleEntity.organization_id,
        ],
        back_populates="organizations",
        cascade="all, delete",
    )

    clients = relationship(
        "ClientEntity",
        secondary="manage.organization_client",
        foreign_keys=[
            OrganizationClientEntity.client_id,
            OrganizationClientEntity.organization_id,
        ],
        back_populates="organizations",
        cascade="all, delete",
    )

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, tenant_id, name="organization_uk_1")
    UniqueConstraint(tenant_id, integration_id, name="organization_uk_2")
