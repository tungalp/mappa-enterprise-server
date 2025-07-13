from dependency_injector import containers
from dependency_injector import providers
from mapa.sso.auth.auth_service import AuthService
from mapa.sso.auth.mail_service import MailService


class ClientContainer(containers.DeclarativeContainer):
    """Auth paketinin bağımlılık konteyneri"""

    # OIDC ile ilgili konfigürasyon parametreleri
    config = providers.Configuration()
    messenger = providers.Dependency()