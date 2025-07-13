from sqlalchemy import Column, Text, UniqueConstraint, JSON,  ForeignKey, Integer
from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship



class MapEntity(EntityMixin, Base):
    """Map Db Model"""

    __tablename__ = "map"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    initial_extent = Column(Text, nullable=False)
    full_extent = Column(Text, nullable=False)
    widget_types = Column(JSON, nullable=True)
    zoom = Column(Integer, nullable=True)
    namespace_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.namespace.id"), nullable=True)
    namespace = relationship("NamespaceEntity")
    srid = Column(Text, nullable=False)

    map_layers = relationship("MapLayerEntity")

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, tenant_id, name='spatial_map_uk_1')
