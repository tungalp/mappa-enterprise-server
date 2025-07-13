from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import (JSON, Column, ForeignKey, Integer, Text,
                        UniqueConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


class MapLayerEntity(EntityMixin, Base):
    """MapLayer Db Model"""

    __tablename__ = "map_layer"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    name = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    parent_id = Column(Text, nullable=True)
    params = Column(JSON, nullable=True)

    map_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.map.id"), nullable=False, index=True)
    map = relationship("MapEntity", backref="map")

    layer_definition_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.layer_definition.id"), nullable=True, index=True)
    layer_definition = relationship("LayerDefinitionEntity")

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(map_id, layer_definition_id, tenant_id,
                     name='spatial_map_layer_uk_1')
