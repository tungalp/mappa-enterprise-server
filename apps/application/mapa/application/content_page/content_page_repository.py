from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.application.content_page.content_page_entity import ContentPageEntity

class ContentPageRepository(BaseRepository[ContentPageEntity]):
    """ContentPage Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ContentPageEntity)
