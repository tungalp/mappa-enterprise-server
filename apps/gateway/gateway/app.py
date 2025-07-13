import pathlib
import gateway
import os
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from gateway.config.app_container import AppContainer, get_all_consumers
from gateway.gateway_api.router import router as gateway_api_router
from gateway.integration.router import router as integration_router
from gateway.parameter_mapping.router import router as parameter_mapping_router
from gateway.connection_info.router import router as connection_info_router
from gateway.route.router import router as route_router
from gateway.context_var.router import router as context_var_router
from mapa.security import OAuth2IdTokenBackend

from mapa.log.elk_middleware import ElkMiddleware
from mapa.alembic.migration import Migration
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from mapa.core.rabbitmq.consumer_runner import ConsumerRunner
import asyncio
from contextlib import asynccontextmanager
import redis.asyncio as aioredis


app_props = {
    "title": "Mapa Gateway",
    "description": "Mapa Gateway",
    "version": "0.0.1",
    "terms_of_service": "http://mapa.com.tr/terms/",
    "contact": {
        "name": "Admin",
        "url": "http://mapa.com.tr/contact/",
        "email": "admin@mapa.com.tr",
    },
    "license_info": {
        "name": "Mapa Commercial Licenze",
        "url": "https://mapa.com.tr/licenses/mapa.html",
    },
    "root_path": "",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_conf = app.container.config()["redis"]

    try:
        write_redis = await aioredis.from_url(
            f"redis://{redis_conf['host']}:{redis_conf['write_port']}",
            password=redis_conf["password"],
            db=redis_conf["db"],
            encoding="utf-8",
        )

        read_redis = await aioredis.from_url(
            f"redis://{redis_conf['host']}:{redis_conf['read_port']}",
            password=redis_conf["password"],
            db=redis_conf["db"],
            encoding="utf-8",
        )

        print(f"write server version: {(await write_redis.info())['redis_version']}")
        print(f"read server version: {(await read_redis.info())['redis_version']}")

        app.state.redis_write = write_redis
        app.state.redis_read = read_redis

        print("Redis bağlantıları başarılı (read & write ayrıldı)")

        runner = ConsumerRunner(
            get_all_consumers(
                app.container, app.state.redis_write, app.state.redis_read
            )
        )
        await runner.start()

        # Outbox worker
        async def worker():
            while True:
                try:
                    await app.container.service_messenger().publish_pending_events()
                except Exception as e:
                    print(f"Outbox worker error: {e}")
                await asyncio.sleep(5)

        asyncio.create_task(worker())
        
    except Exception as e:
        print(f"Redis bağlantı hatası: {e}")

    yield

    if write_redis:
        await write_redis.close()

    if read_redis:
        await read_redis.close()


def create_application():
    """FastAPI uygulamasını oluşturur"""

    # Konteyner
    container = AppContainer()
    container.wire(packages=[gateway])
    sanitize_raw = container.config.apm.sanitize_field_names()
    sanitize_list = [item.strip() for item in sanitize_raw.split(",") if item.strip()]
    ignore_urls = ["/health*"]
    # Elastic-apm
    apm = make_apm_client(
        {
            "SERVICE_NAME": container.config.apm.service_name(),
            "SECRET_TOKEN": container.config.apm.secret_token(),
            "SERVER_URL": container.config.apm.server_url(),
            "ENVIRONMENT": container.config.apm.environment(),
            "CAPTURE_BODY": container.config.apm.body(),
            "LOG_LEVEL": container.config.apm.log_level(),
            "SANITIZE_FIELD_NAMES": sanitize_list,
            "TRANSACTION_IGNORE_URLS": ignore_urls
        }
    )

    middleware = [
        Middleware(
            AuthenticationMiddleware,
            backend=OAuth2IdTokenBackend(jwks_uri=container.config.oidc()["jwks_uri"]),
        ),
        # Middleware(ElasticAPM, client=apm),
        # Middleware(
        #     ElkMiddleware,
        #     application_name="GATEWAY",
        #     host=container.config.elk.host(),
        #     port=container.config.elk.port(),
        #     env=os.environ.get("MAPA_ENV"),
        #     redact_fields=sanitize_list,
        #     excluded_paths=ignore_urls,
        # ),
    ]
    # Ana uygulama nesnesi
    application = FastAPI(
        **app_props, middleware=middleware, redirect_slashes=False, lifespan=lifespan
    )
    application.container = container  # type: ignore

    application.apm_client = apm  # type: ignore

    # Routes
    application.include_router(
        gateway_api_router, prefix="/api/gateway/gateway_api", tags=["gateway_api"]
    )

    application.include_router(
        integration_router, prefix="/api/gateway/integration", tags=["integration"]
    )

    application.include_router(
        parameter_mapping_router,
        prefix="/api/gateway/parameter_mapping",
        tags=["parameter_mapping"],
    )

    application.include_router(
        route_router, prefix="/api/gateway/route", tags=["route"]
    )

    application.include_router(
        connection_info_router,
        prefix="/api/gateway/connection_info",
        tags=["connection_info"],
    )

    application.include_router(
        context_var_router, prefix="/api/gateway/context_var", tags=["context_var"]
    )

    migration = Migration(
        str(pathlib.Path(__file__).parent.parent / "migrations"), container.config.alembic()["url"]
    )
    migration.upgrade_migrations()

    return application
