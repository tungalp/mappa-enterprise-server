from sqlalchemy import Column, Text, UniqueConstraint
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from mapa.manage.api_scope.api_scope_entity import ApiScopeEntity
from mapa.manage.organization_role.organization_role_entity import OrganizationRoleEntity
from mapa.manage.role_user.role_user_entity import RoleUserEntity
from mapa.manage.role_api_scope.role_api_scope_entity import RoleApiScopeEntity

class UserVariableTypeEntity(EntityMixin, Base):
    """UserVariableType Db Model"""

    __tablename__ = "user_variable_type"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    name = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, tenant_id, name='user_variable_type_uk_1')