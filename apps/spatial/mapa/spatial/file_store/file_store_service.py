from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.file_store.file_store_model import CreateFileStore, UpdateAllFileStore, UpdateFileStore, FileStore
from mapa.spatial.file_store.file_store_repository import FileStoreRepository


class FileStoreService(BaseEntityService[FileStoreRepository, FileStore, CreateFileStore, UpdateFileStore, UpdateAllFileStore]):
    """FileStore Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, FileStoreRepository, FileStore)
