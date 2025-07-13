from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.bookmark.bookmark_entity import BookmarkEntity


class BookmarkRepository(BaseRepository[BookmarkEntity]):
    """Bookmark Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, BookmarkEntity)
