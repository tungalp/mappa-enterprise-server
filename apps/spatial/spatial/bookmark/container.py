from dependency_injector import containers, providers
from mapa.spatial.bookmark.bookmark_service import BookmarkService


class BookmarkContainer(containers.DeclarativeContainer):
    """Bookmark paketinin bağımlılık konteyneri

    """
    database = providers.Dependency()

    bookmark_service = providers.Factory(
        BookmarkService,
        async_db=database,
    )
