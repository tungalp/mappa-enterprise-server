from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.sso.refresh_token.refresh_token_model import CreateRefreshToken, RefreshToken, UpdateAllRefreshToken, UpdateRefreshToken
from mapa.sso.refresh_token.refresh_token_repository import RefreshTokenRepository


class RefreshTokenService(BaseEntityService[
    RefreshTokenRepository, RefreshToken, CreateRefreshToken, UpdateRefreshToken, UpdateAllRefreshToken]):
    """RefreshToken servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RefreshTokenRepository, RefreshToken)

