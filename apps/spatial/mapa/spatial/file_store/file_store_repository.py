from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.spatial.file_store.file_store_entity import FileStoreEntity


class FileStoreRepository(BaseRepository[FileStoreEntity]):
    """FileStore Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, FileStoreEntity)
