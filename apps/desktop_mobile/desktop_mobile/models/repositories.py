from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from desktop_mobile.models.entities import (
    CollectionEntity,
    MapEntity,
    LayerEntity,
    ApiKeyEntity,
    ApiKeyPermissionEntity
)

class CollectionRepository(BaseRepository[CollectionEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, CollectionEntity)

class MapRepository(BaseRepository[MapEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, MapEntity)

class LayerRepository(BaseRepository[LayerEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, LayerEntity)

class ApiKeyRepository(BaseRepository[ApiKeyEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ApiKeyEntity)

class ApiKeyPermissionRepository(BaseRepository[ApiKeyPermissionEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ApiKeyPermissionEntity)
