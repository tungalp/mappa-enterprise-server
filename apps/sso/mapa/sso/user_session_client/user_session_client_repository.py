from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.sso.user_session_client.user_session_client_entity import UserSessionClientEntity


class UserSessionClientRepository(BaseRepository[UserSessionClientEntity]):
    """UserSessionClient Repo"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, UserSessionClientEntity)
    