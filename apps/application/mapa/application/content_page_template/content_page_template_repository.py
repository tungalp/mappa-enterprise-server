from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.application.content_page_template.content_page_template_entity import ContentPageTemplateEntity

class ContentPageTemplateRepository(BaseRepository[ContentPageTemplateEntity]):
    """ContentPageTemplate Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ContentPageTemplateEntity)
