from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Text,
    ForeignKey,
    Numeric,
    ARRAY,
    Uuid,
    DateTime,
)
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType
from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy_utils import UUIDType
from mapa.manage.organization.organization_entity import OrganizationEntity
from mapa.manage.organization_user.organization_user_entity import OrganizationUserEntity
from mapa.manage.role.role_entity import RoleEntity
from mapa.manage.role_user.role_user_entity import RoleUserEntity


# NOT : (19.07.2023)
# User register edilirken ya da davetiye ile gelen user register edilirken subject_id alanı boş kaydediliyordu. ID alanı insertten sonra dolduğu için.
# EntityMixin kaldırılarak id ve created_at bilgileri içeri alınmıştır.
# User entity si oluşturulurken id bilgisi üretilip subject_id de aynı bilgiyi kullanabilmektedir.
def mydefault(column_name):
    if column_name == "id":
        return uuid.uuid4
    if column_name == "subject_id":
        return lambda ctx: str(ctx.current_parameters.get("id"))


class UserEntity(Base):
    """User Entity"""

    __tablename__ = "user"  # type: ignore
    __table_args__ = {"schema": "manage"}

    id = Column(Uuid(), primary_key=True, default=mydefault("id"), insert_sentinel=True)
    created_at = Column(DateTime, default=func.now())
    subject_id = Column(
        Text, nullable=False, unique=True, index=True, default=mydefault("subject_id")
    )

    source = Column(Text, nullable=False, default="local")
    name = Column(Text, nullable=False)
    surname = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True, index=True)
    password = Column(Text, nullable=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    phone = Column(Text, nullable=True)

    # Kullanıcının first_party uygulamalarda en son hangi tenant ı kullandığı bilgisi
    last_tenant_id = Column(UUIDType(binary=False), nullable=True)

    # Kullanıcının dahil olduğu tenant listesi
    tenant_users = relationship(
        "TenantUserEntity", back_populates="user", cascade="all, delete-orphan"
    )

    # Kullanıcının sahip olduğu tenant
    tenant = relationship(
        "TenantEntity",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    provider = Column(Text, nullable=True)
    provider_user_id = Column(UUIDType(binary=False), nullable=True)
    profile_adaptor_id = Column(UUIDType(binary=False), nullable=True)

    is_ldap_user = Column(Boolean, nullable=True, default=False)
    ldap_server_id = Column(
        UUIDType(binary=False),
        ForeignKey("manage.ldap_server.id", ondelete="CASCADE"),
        nullable=True,
    )
    ldap_server = relationship("LdapServerEntity")

    roles = relationship(
        RoleEntity,
        secondary="manage.role_user",
        foreign_keys=[RoleUserEntity.user_id, RoleUserEntity.role_id],
        back_populates="users",
        cascade="all, delete",
        overlaps="users",
    )

    organizations = relationship(
        OrganizationEntity,
        secondary="manage.organization_user",
        foreign_keys=[
            OrganizationUserEntity.user_id,
            OrganizationUserEntity.organization_id,
        ],
        back_populates="users",
        cascade="all, delete",
        overlaps="users",
    )

    blocked = Column(Boolean, nullable=False, default=False)
    picture = Column(Text, nullable=True)
    openid = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    given_name = Column(Text, nullable=True)
    family_name = Column(Text, nullable=True)
    nickname = Column(Text, nullable=True)
    offline_access = Column(Boolean, nullable=True)

    context = Column(JSON, nullable=True)
