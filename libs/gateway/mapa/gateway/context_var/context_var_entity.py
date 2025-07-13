from sqlalchemy import JSON, Column, Text, UniqueConstraint, Boolean
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy_utils import UUIDType


class ContextVarEntity(EntityMixin, TenantMixin, Base):
    """Context Variables Db Model"""

    __tablename__ = "context_var"  # type: ignore

    __table_args__ = {'schema': 'gateway'}

    key = Column(Text, nullable=False)
    value = Column(JSON, nullable=False)
    
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(key, tenant_id, name='gateway_context_var_key_tenant_id_uk')