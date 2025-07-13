from dependency_injector import containers
from dependency_injector import providers
from mapa.manage.invitation.invitation_util_service import InvitationUtilService
from mapa.manage.invitation.mail_service import MailService
from mapa.manage.user.user_service import UserService

class UserContainer(containers.DeclarativeContainer):
    """User paketinin bağımlılık konteyneri

    """
    
    # OIDC ile ilgili konfigürasyon parametreleri
    config = providers.Configuration()
    
    database = providers.Dependency()
    
    api_service = providers.Dependency()
    organization_service = providers.Dependency()
    user_service = providers.Factory(
        UserService,
        async_db=database,
        api_service=api_service,
        organization_service=organization_service
    )
    
