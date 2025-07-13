from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.tenant_client.tenant_client_entity import TenantClientEntity


class TenantClientRepository(BaseRepository[TenantClientEntity]):
    """TenantUser Repo"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, TenantClientEntity)
    