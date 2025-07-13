from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import (JSON, Boolean, Column, REAL, ForeignKey, Integer,
                        Text, UniqueConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


class LayerEntity(EntityMixin, Base):
    """Layer Db Model"""

    __tablename__ = "layer"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    name = Column(Text, nullable=False)
    code = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    default_extent = Column(Text, nullable=True)

    max_scale = Column(Integer, nullable=True)
    min_scale = Column(Integer, nullable=True)
    opacity = Column(REAL(precision=1), nullable=True)

    timer = Column(Boolean, nullable=True)
    visible = Column(Boolean, nullable=True)

    field_params = Column(JSON, nullable=True)
    geometry_field_param = Column(JSON, nullable=True)
    style_params = Column(JSON, nullable=True)

    connection_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.connection.id"), nullable=False, index=True)
    connection = relationship("ConnectionEntity")
    
    data_type = Column(Text, nullable=False)
    key_field = Column(Text, nullable=False)
    type_name = Column(Text, nullable=False)
    target_namespace = Column(Text, nullable=True)

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, connection_id, tenant_id, name='spatial_layer_uk_1')
