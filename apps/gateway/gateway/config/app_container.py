import os
import pathlib
from dependency_injector import containers
from dependency_injector import providers
from mapa.core.data import AsyncDatabase
from mapa.gateway.gateway_api.gateway_util_service import GatewayUtilService
from gateway.context_var.container import ContextVarContainer
from gateway.gateway_api.container import GatewayApiContainer
from gateway.connection_info.container import ConnectionInfoContainer
from gateway.integration.container import IntegrationContainer
from gateway.outbox.container import OutboxContainer
from gateway.parameter_mapping.container import ParameterMappingContainer
from gateway.route.container import RouteContainer
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


def get_all_consumers(container, rredis, wredis) -> list:
    connection = container.rabbit_connection()

    return [
        RouteFindConsumer(
            container.route_package().route_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        RoutePagingConsumer(
            container.route_package().route_service(), connection=connection, rredis=rredis, wredis=wredis
        ),
        RouteGetConsumer(
            container.route_package().route_service(), connection=connection, rredis=rredis, wredis=wredis
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

    gateway_api_package = providers.Container(
        GatewayApiContainer, database=db.provided, messenger=service_messenger
    )

    route_package = providers.Container(RouteContainer, database=db.provided)

    integration_package = providers.Container(
        IntegrationContainer, database=db.provided
    )

    parameter_mapping_package = providers.Container(
        ParameterMappingContainer, database=db.provided
    )

    connection_info_package = providers.Container(
        ConnectionInfoContainer, database=db.provided
    )

    context_var_package = providers.Container(ContextVarContainer, database=db.provided)

    gateway_util_service = providers.Singleton(
        GatewayUtilService,
        gateway_api_service=gateway_api_package.gateway_api_service,
        route_service=route_package.route_service,
        integration_service=integration_package.integration_service,
        parameter_mapping_service=parameter_mapping_package.parameter_mapping_service,
        connection_info_service=connection_info_package.connection_info_service,
        messenger=service_messenger,
    )

    gateway_package = providers.Container(
        GatewayApiContainer,
        database=db.provided,
        gateway_util_service=gateway_util_service,
        messenger=service_messenger,
    )
