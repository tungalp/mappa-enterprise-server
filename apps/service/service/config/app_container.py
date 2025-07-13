import os
import pathlib
from dependency_injector import containers
from dependency_injector import providers
from mapa.core.data import AsyncDatabase
from service.outbox.container import OutboxContainer
from service.root.container import RootContainer
from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.message_bus import MessageBus
from mapa.gateway.messaging.producer.service_messenger import ServiceMessenger
from mapa.gateway.messaging.consumer.consumers import (
    RouteFindConsumer,
    RoutePagingConsumer,
    RouteGetConsumer,
)


def get_config_file_names():
    """Geliştirme ya da gerçek ortama göre konfigürasyon dosyasını getirir."""
    config_path = str(pathlib.Path(__file__).parent.resolve())
    config_file_name = config_path + "/config.prod.yml"
    env = os.environ.get("MAPA_ENV")
    if env == "DEVELOPMENT":
        config_file_name = config_path + "/config.dev.yml"
    return [config_path + "/config.yml", config_file_name]


def get_all_consumers(container) -> list:
    connection = container.rabbit_connection()

    return [
        RouteFindConsumer(
            container.route_package().route_service(), connection=connection
        ),
        RoutePagingConsumer(
            container.route_package().route_service(), connection=connection
        ),
        RouteGetConsumer(
            container.route_package().route_service(), connection=connection
        ),
    ]


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

    # Root package
    root_package = providers.Container(
        RootContainer, database=db.provided, messenger=service_messenger
    )
