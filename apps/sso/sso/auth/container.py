from dependency_injector import containers
from dependency_injector import providers
from mapa.sso.auth.auth_service import AuthService
from mapa.sso.auth.mail_service import MailService


class AuthContainer(containers.DeclarativeContainer):
    """Auth paketinin bağımlılık konteyneri"""

    # OIDC ile ilgili konfigürasyon parametreleri
    config = providers.Configuration()

    authorize_validator = providers.Dependency()
    user_session_service = providers.Dependency()
    user_session_client_service = providers.Dependency()
    consent_service = providers.Dependency()
    messenger = providers.Dependency()

    auth_service = providers.Factory(
        AuthService,
        jwt_secret=config.oidc.jwt_secret,
        session_timeout=config.session.timeout,
        authorize_validator=authorize_validator,
        user_session_service=user_session_service,
        user_session_client_service=user_session_client_service,
        consent_service=consent_service,
        messenger = messenger
    )

    mail_service = providers.Factory(
        MailService,
        smtp=config.mail.smtp,
        port=config.mail.port,
        user_name=config.mail.user_name,
        password=config.mail.password,
        method=config.mail.method,
    )
