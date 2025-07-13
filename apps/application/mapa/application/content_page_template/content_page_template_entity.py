from sqlalchemy import Column, Text, JSON
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from mapa.application.constants import ContentPageType


class ContentPageTemplateEntity(EntityMixin, TenantMixin, Base):
    """ContentPageTemplate Db Model"""

    __tablename__ = "content_page_template"  # type: ignore

    __table_args__ = {'schema': 'application'}

    name = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Text, nullable=False, default=ContentPageType.PAGE)
    designer_schema = Column(JSON, nullable=False)
