from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import Column, Text, UniqueConstraint
from sqlalchemy_utils import UUIDType


class NamespaceEntity(EntityMixin, Base):
    """Namespace Db Model"""

    __tablename__ = "namespace"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    identifier = Column(Text, nullable=False)

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, identifier, tenant_id,
                     name='spatial_namespace_uk_1')
