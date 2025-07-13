from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.sso.consent.consent_entity import ConsentEntity


class ConsentRepository(BaseRepository[ConsentEntity]):
    """Consent Repo"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ConsentEntity)
    