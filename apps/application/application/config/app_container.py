import os
import pathlib
from dependency_injector import containers
from dependency_injector import providers
from application.content_page.container import ContentPageContainer
from application.apps.container import AppContainer
from application.content_page_template.container import ContentPageTemplateContainer
from application.outbox.container import OutboxContainer
from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.message_bus import MessageBus
from mapa.application.messaging.producer.service_messenger import ServiceMessenger
from mapa.core.data import AsyncDatabase


def get_config_file_names():
    """Geliştirme ya da gerçek ortama göre konfigürasyon dosyasını getirir."""
    config_path = str(pathlib.Path(__file__).parent.resolve())
    config_file_name = config_path + "/config.prod.yml"
    env = os.environ.get("MAPA_ENV")
    if env == "DEVELOPMENT":
        config_file_name = config_path + "/config.dev.yml"
    return [config_path + "/config.yml", config_file_name]


class ApplicationContainer(containers.DeclarativeContainer):
    """Genel uygulama servis ve DI konteyner yapısı.
    Uygulamadaki veritabanı bağlantısı, alt konteynerlar ve bunların
    birbirlerine olan bağımlılıkları burada tanımlanır.
    """

    config = providers.Configuration(yaml_files=get_config_file_names(), strict=True)

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

    content_page_template_package = providers.Container(
        ContentPageTemplateContainer, database=db.provided
    )

    content_page_package = providers.Container(
        ContentPageContainer, database=db.provided
    )

    app_package = providers.Container(
        AppContainer,
        database=db.provided,
        messenger=service_messenger,
        content_page_service=content_page_package.content_page_service,
    )
