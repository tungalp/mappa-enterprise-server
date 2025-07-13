import os
import pathlib
from dependency_injector import containers
from dependency_injector import providers
from sso.outbox.container import OutboxContainer
from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.message_bus import MessageBus
from mapa.sso.auth.auth_util_service import AuthUtilService
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from sso.client.container import ClientContainer
from sso.ping.container import PingContainer
from sso.consent.container import ConsentContainer
from sso.tenant.container import TenantContainer
from sso.user.container import UserContainer
from sso.user_session.container import UserSesionContainer
from mapa.core.data import AsyncDatabase
from sso.oidc.container import OidcContainer
from sso.auth.container import AuthContainer


def get_config_file_names():
    """Geliştirme ya da gerçek ortama göre konfigürasyon dosyasını getirir."""
    config_path = str(pathlib.Path(__file__).parent.resolve())
    config_file_name = config_path + "/config.prod.yml"
    env = os.environ.get("MAPA_ENV")
    if env == "DEVELOPMENT":
        config_file_name = config_path + "/config.dev.yml"
    return [config_path + "/config.yml", config_file_name]


class AppContainer(containers.DeclarativeContainer):
    """Genel uygulama servis ve DI konteyner yapısı.
    Uygulamadaki veritabanı bağlantısı, alt konteynerlar ve bunların
    birbirlerine olan bağımlılıkları burada tanımlanır.
    """

    # Genel uygulama konfigürasyon bilgileri
    config = providers.Configuration(yaml_files=get_config_file_names(), strict=True)

    # Veritabanı
    db = providers.Singleton(AsyncDatabase, db_url=config.db.url)

    outbox_package = providers.Container(OutboxContainer, database=db.provided)

    rabbit_connection = providers.Singleton(RabbitConnection, config=config.rabbitmq)

    message_bus = providers.Singleton(
        MessageBus,
        exchange_name=config.rabbitmq.exchange_name,
        connection=rabbit_connection,
    )

    service_messenger = providers.Singleton(
        ServiceMessenger,
        message_bus=message_bus,
        outbox_service=outbox_package.outbox_service,
        async_db=db.provided,
    )

    # Util Service
    util_service = providers.Singleton(
        AuthUtilService, jwt_secret=config.oidc.jwt_secret
    )

    # Ping pacakge
    ping_package = providers.Container(PingContainer, database=db.provided)

    user_session_package = providers.Container(
        UserSesionContainer, database=db.provided
    )

    consent_package = providers.Container(ConsentContainer, database=db.provided)

    oidc_package = providers.Container(
        OidcContainer,
        database=db.provided,
        config=config,
        consent_service=consent_package.consent_service,
        user_session_service=user_session_package.user_session_service,
        user_session_client_service=user_session_package.user_session_client_service,
        util_service=util_service,
        messenger=service_messenger,
    )

    auth_package = providers.Container(
        AuthContainer,
        config=config,
        authorize_validator=oidc_package.authorize_validator,
        user_session_service=user_session_package.user_session_service,
        user_session_client_service=user_session_package.user_session_client_service,
        consent_service=consent_package.consent_service,
        messenger=service_messenger,
    )

    tenant_package = providers.Container(
        TenantContainer,
        messenger=service_messenger,
    )

    user_package = providers.Container(
        UserContainer,
        messenger=service_messenger,
    )

    client_package = providers.Container(ClientContainer, messenger=service_messenger)
