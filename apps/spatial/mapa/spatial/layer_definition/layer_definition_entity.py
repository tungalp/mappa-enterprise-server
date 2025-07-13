from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


class LayerDefinitionEntity(EntityMixin, Base):
    """LayerDefinition Db Model"""

    __tablename__ = "layer_definition"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    layer_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.layer.id"),  nullable=False, index=True)

    definition_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.definition.id"), nullable=True)

    layer = relationship("LayerEntity")
    definition = relationship("DefinitionEntity")
    layer_hooks = relationship("LayerHookEntity")

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(layer_id, definition_id, tenant_id,
                     name='spatial_layer_definition_uk_1')
