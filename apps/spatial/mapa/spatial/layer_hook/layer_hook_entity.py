from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import Column, ForeignKey, Text, UniqueConstraint
from sqlalchemy_utils import UUIDType


class LayerHookEntity(EntityMixin, Base):
    """LayerHook Db Model"""

    __tablename__ = "layer_hook"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    route_id = Column(UUIDType(binary=False), nullable=False)
    layer_definition_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.layer_definition.id"), nullable=False)

    widget_name = Column(Text, nullable=False)
    hook_operation_type = Column(Text, nullable=False)

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(layer_definition_id, widget_name, hook_operation_type, tenant_id,
                     name='spatial_layer_hook_uk_1')
