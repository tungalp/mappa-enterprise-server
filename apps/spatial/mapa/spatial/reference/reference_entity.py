from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import Column, Text, UniqueConstraint
from sqlalchemy_utils import UUIDType


class ReferenceEntity(EntityMixin, Base):
    """Reference Db Model"""

    __tablename__ = "reference"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    epsgcode = Column(Text, nullable=False)
    wkid = Column(Text, nullable=False)
    wkt = Column(Text, nullable=False)
    projcs = Column(Text, nullable=False)
    name = Column(Text, nullable=False)

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(epsgcode, tenant_id, name='spatial_reference_uk_1')
    UniqueConstraint(name, tenant_id, name='spatial_reference_uk_2')
