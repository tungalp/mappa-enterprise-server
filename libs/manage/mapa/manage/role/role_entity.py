from sqlalchemy import Column, Text, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from mapa.manage.api_scope.api_scope_entity import ApiScopeEntity
from mapa.manage.organization_role.organization_role_entity import OrganizationRoleEntity
from mapa.manage.role_user.role_user_entity import RoleUserEntity
from mapa.manage.role_api_scope.role_api_scope_entity import RoleApiScopeEntity

class RoleEntity(EntityMixin, Base):
    """Role Db Model"""

    __tablename__ = "role"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    users = relationship("UserEntity",secondary="manage.role_user",
                         foreign_keys=[RoleUserEntity.user_id, RoleUserEntity.role_id],back_populates="roles",cascade="all, delete" )

    api_scopes = relationship(ApiScopeEntity,secondary="manage.role_api_scope",
                         foreign_keys=[RoleApiScopeEntity.api_scope_id,RoleApiScopeEntity.role_id],backref="role",cascade="all, delete")
    
    organizations = relationship("OrganizationEntity",secondary="manage.organization_role",
                         foreign_keys=[OrganizationRoleEntity.organization_id, OrganizationRoleEntity.role_id],back_populates="roles",cascade="all, delete" )

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, tenant_id, name='role_uk_1')