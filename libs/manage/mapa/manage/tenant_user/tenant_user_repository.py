from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.tenant_user.tenant_user_entity import TenantUserEntity

class TenantUserRepository(BaseRepository[TenantUserEntity]):
    """TenantUser Repo"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, TenantUserEntity)
    