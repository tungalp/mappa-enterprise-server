from typing import Any, Dict, List
from uuid import UUID, uuid4

from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.result import PagingResult
from mapa.spatial.bookmark.bookmark_model import (Bookmark, CreateBookmark,
                                                 UpdateAllBookmark,
                                                 UpdateBookmark)
from mapa.spatial.bookmark.bookmark_repository import BookmarkRepository


class BookmarkService(BaseEntityService[BookmarkRepository, Bookmark, CreateBookmark, UpdateBookmark, UpdateAllBookmark]):
    """Bookmark Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, BookmarkRepository, Bookmark)

    async def find_by_user_id(self, user_id: UUID) -> List[Bookmark]:
        """Kullanının Bookmarklarını getirir."""

        return await self.find(QueryArgs(
            where=[Filter(field="user_id", op=FilterOp.EQUAL, value=user_id)]
        ))

    async def paging(self, query_args: QueryArgs, user_id: str | None = None,tenant_id: str | None = None) -> PagingResult[Bookmark]:

        user_filter: Filter = Filter(
            field="user_id", op=FilterOp.EQUAL, value=user_id)

        if query_args.where == None:
            query_args.where = []

        query_args.where.append(user_filter)
        bookmark = await super().paging(query_args, tenant_id)
        return bookmark

    async def get(self, user_id: str, bookmark_id: str, tenant_id: str | None = None, field_list: List[str | Dict[str, Any]] | None = None) -> Bookmark:

        bookmark : Bookmark = await super().get(uuid4(), tenant_id, field_list)
        user_bookmark_list = await self.find_by_user_id(UUID(user_id))
        for book in user_bookmark_list:
            if book.id == UUID(bookmark_id):
                bookmark = await super().get(bookmark_id, tenant_id, field_list)
                break

        return bookmark

    async def create(self, user_id: str,  bookmark: CreateBookmark,  tenant_id: str | None = None) -> Bookmark:

        if user_id != None:
            bookmark.user_id = UUID(user_id)
            created_bookmark = await super().create(bookmark, tenant_id)
        else:
            raise ValueError(f"userIdIsNone")
        return created_bookmark

    async def create_all(self, user_id: str, bookmarks: List[CreateBookmark],   tenant_id: str | None = None) -> List[Bookmark]:

        if user_id != None:
            for book in bookmarks:
                book.user_id = UUID(user_id)
            created_bookmarks = await super().create_all(bookmarks, tenant_id)
        else:
            raise ValueError(f"userIdIsNone")
        return created_bookmarks
