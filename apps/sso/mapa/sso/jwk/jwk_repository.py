from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.sso.jwk.jwk_entity import JwkEntity


class JwkRepository(BaseRepository[JwkEntity]):
    """Jwks Repo"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, JwkEntity)
    