from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.sso.user_session.user_session_entity import UserSessionEntity


class UserSessionRepository(BaseRepository[UserSessionEntity]):
    """UserSession Repo"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, UserSessionEntity)
    