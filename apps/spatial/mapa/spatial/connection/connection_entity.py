from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import JSON, Column, Text, UniqueConstraint
from sqlalchemy_utils import UUIDType


class ConnectionEntity(EntityMixin, Base):
    """Connection Db Model"""

    __tablename__ = "connection"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    route_params = Column(JSON, nullable=False)
    type = Column(Text, nullable=False)

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, tenant_id, name='spatial_connection_uk_1')
