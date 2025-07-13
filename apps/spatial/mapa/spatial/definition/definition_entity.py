from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy import JSON, Boolean, Column, REAL, Float, Integer, Text


class DefinitionEntity(EntityMixin, TenantMixin, Base):
    """Definition Db Model"""

    __tablename__ = "definition"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    title = Column(Text, nullable=True)
    default_extent = Column(Text, nullable=True)
    max_scale = Column(Integer, nullable=True)
    min_scale = Column(Integer, nullable=True)
    opacity = Column(REAL(precision=1), nullable=True)
    timer = Column(Boolean, nullable=True)
    is_attribute_panel = Column(Boolean, nullable=True)
    organization_geo_constraint = Column(Boolean, nullable=True)
    is_base_layer = Column(Boolean, nullable=True)

    field_params = Column(JSON, nullable=True)
    style_params = Column(JSON, nullable=True)
    topology_rules_params = Column(JSON, nullable=True)
    filter_params = Column(JSON, nullable=True)

    edit_snap_scale = Column(Integer, nullable=True)
    data_type = Column(Text, nullable=False)
    key_field = Column(Text, nullable=False)
    type_name = Column(Text, nullable=False)
    target_namespace = Column(Text, nullable=True)
