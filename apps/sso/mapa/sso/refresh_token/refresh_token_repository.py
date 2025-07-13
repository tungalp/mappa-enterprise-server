from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.sso.refresh_token.refresh_token_entity import RefreshTokenEntity


class RefreshTokenRepository(BaseRepository[RefreshTokenEntity]):
    """RefreshToken Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RefreshTokenEntity)
