from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import Column, Text, UniqueConstraint


class HookEntity(EntityMixin, Base):
    """Hook Db Model"""

    __tablename__ = "hook"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    type = Column(Text, nullable=False)
    operation_type = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    UniqueConstraint(type, operation_type,
                     name='spatial_hook_uk_1')
