from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.manage.profile_adaptor.profile_adaptor_model import CreateProfileAdaptor, UpdateAllProfileAdaptor, UpdateProfileAdaptor, ProfileAdaptor
from mapa.manage.profile_adaptor.profile_adaptor_repository import ProfileAdaptorRepository

class ProfileAdaptorService(BaseEntityService[ProfileAdaptorRepository, ProfileAdaptor, CreateProfileAdaptor, UpdateProfileAdaptor, UpdateAllProfileAdaptor]):
    """ProfileAdaptor Servisi"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ProfileAdaptorRepository, ProfileAdaptor)

    
    async def get_by_profile_adaptor_id(self, profile_adaptor_id: UUID, tenant_id: str = None) -> ProfileAdaptor:  # type: ignore
        """ID ye göre bilgilerini getirir."""

        return await self.get(profile_adaptor_id, tenant_id)