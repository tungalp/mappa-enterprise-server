from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.sso.user_session.user_session_model import CreateUserSession, UpdateAllUserSession, UpdateUserSession, UserSession
from mapa.sso.user_session.user_session_repository import UserSessionRepository


class UserSessionService(BaseEntityService[UserSessionRepository, UserSession, CreateUserSession, UpdateUserSession, UpdateAllUserSession]):
    """Kullanıcı Oturum Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, UserSessionRepository, UserSession)
