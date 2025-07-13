from sqlalchemy import ARRAY, Boolean, Column, Text, UniqueConstraint, JSON, ForeignKey
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from mapa.application.constants import ContentPageType
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from nanoid import generate


class ContentPageEntity(EntityMixin, TenantMixin, Base):
    """ContentPage Db Model"""

    __tablename__ = "content_page"  # type: ignore

    __table_args__ = {'schema': 'application'}

    name = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Text, nullable=False, default=ContentPageType.PAGE)
    scope = Column(Text, nullable=True)
    designer_schema = Column(JSON, nullable=False)
    path = Column(Text, nullable=True)
    query = Column(Text, nullable=True)
    app_id = Column(UUIDType(binary=False), ForeignKey(
        "application.app.id", ondelete="CASCADE"), nullable=False, index=True)
    app = relationship("AppEntity", back_populates="content_page")
    UniqueConstraint(name, app_id, name='content_page_uk_1')
