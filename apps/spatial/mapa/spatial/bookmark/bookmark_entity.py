from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import Column, ForeignKey, Text, UniqueConstraint
from sqlalchemy_utils import UUIDType


class BookmarkEntity(EntityMixin, Base):
    """Bookmark Db Model"""

    __tablename__ = "bookmark"  # type: ignore
    __table_args__ = {'schema': 'spatial'}

    name = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    thumbnail = Column(Text, nullable=True)

    map_id = Column(UUIDType(binary=False), ForeignKey(
        "spatial.map.id"), nullable=False, index=True)

    user_id = Column(UUIDType(binary=False), nullable=False)

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, map_id, user_id, tenant_id,
                     name='spatial_bookmark_uk_1')
