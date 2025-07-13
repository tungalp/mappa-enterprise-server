from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


class MapBaseLayerEntity(EntityMixin, Base):
    """MapBaseLayer Db Model"""

    __tablename__ = "map_base_layer"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    order = Column(Integer, nullable=False)

    map_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.map.id"), nullable=False, index=True)
    map = relationship("MapEntity")
    
    base_layer_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.base_layer.id"), nullable=False, index=True)
    base_layer = relationship("BaseLayerEntity")

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(map_id, base_layer_id, tenant_id, name='spatial_map_base_layer_uk_1')
