from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy import JSON, Column, Text


class BaseLayerEntity(EntityMixin, TenantMixin, Base):
    """BaseLayer Db Model"""

    __tablename__ = "base_layer"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    type = Column(Text, nullable=False)
    connection = Column(JSON, nullable=True)
