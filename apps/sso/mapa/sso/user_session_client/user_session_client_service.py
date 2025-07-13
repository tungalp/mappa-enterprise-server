from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.sso.user_session_client.user_session_client_model import CreateUserSessionClient, UpdateAllUserSessionClient, UpdateUserSessionClient, UserSessionClient
from mapa.sso.user_session_client.user_session_client_repository import UserSessionClientRepository


class UserSessionClientService(BaseEntityService[UserSessionClientRepository, UserSessionClient, CreateUserSessionClient, UpdateUserSessionClient, UpdateAllUserSessionClient]):
    """Kullanıcı Oturum Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, UserSessionClientRepository, UserSessionClient)


    async def find_by_client(self, user_session_id: UUID, client_id: UUID) -> UserSessionClient | None:
        """UserSession ve Client a göre sorgulama yapar"""
        
        return await self.find_one(QueryArgs(
            where=[
                Filter(field="user_session_id", op=FilterOp.EQUAL, value=user_session_id),
                Filter(field="client_id", op=FilterOp.EQUAL, value=client_id)
            ]
        ))