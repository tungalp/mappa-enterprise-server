from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.tenant.tenant_entity import TenantEntity


class TenantRepository(BaseRepository[TenantEntity]):
    """Tenant Repo"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, TenantEntity)
