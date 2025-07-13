from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.sso.authorization_code.authorization_code_entity import AuthorizationCodeEntity


class AuthorizationCodeRepository(BaseRepository[AuthorizationCodeEntity]):
    """AuthorizationCode Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, AuthorizationCodeEntity)
