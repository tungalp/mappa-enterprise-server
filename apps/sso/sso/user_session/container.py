from dependency_injector import containers
from dependency_injector import providers

from mapa.sso.user_session import UserSessionService
from mapa.sso.user_session_client.user_session_client_service import UserSessionClientService


class UserSesionContainer(containers.DeclarativeContainer):
    """Kullanıcı Oturum konfigürasyonu"""

    database = providers.Dependency()

    user_session_service = providers.Factory(
        UserSessionService,
        async_db=database
    )
    
    user_session_client_service = providers.Factory(
        UserSessionClientService,
        async_db=database
    )
