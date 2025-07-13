import pathlib
from mapa.core.rabbitmq.consumer_runner import ConsumerRunner
import manage
import os
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from manage.check_redirect_uris import check_redirect_uris
from manage.config.app_container import AppContainer, get_all_consumers
from manage.ping.router import router as ping_router
from manage.role.router import router as role_router
from manage.client.router import router as client_router
from manage.client_api_scope.router import router as client_api_scope_router
from manage.api_scope.router import router as api_scope_router
from manage.api.router import router as api_router
from manage.client_api.router import router as client_api_router
from manage.user.router import router as user_router
from manage.role_user.router import router as role_user_router
from manage.role_api_scope.router import router as role_api_scope_router
from manage.profile_adaptor.router import router as profile_adaptor_router
from manage.invitation.router import router as invitation_router
from manage.tenant.router import router as tenant_router
from manage.organization.router import router as organization_router
from manage.organization_user.router import router as organization_user_router
from manage.organization_type.router import router as organization_type_router
from manage.organization_role.router import router as organization_role_router
from manage.organization_client.router import router as organization_client_router
from manage.user_variable_type.router import router as user_variable_type_router
from manage.ldap_server.router import router as ldap_server_router
from mapa.security import OAuth2IdTokenBackend
from mapa.log.elk_middleware import ElkMiddleware

from mapa.alembic.migration import Migration
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from contextlib import asynccontextmanager
from redis import asyncio as aioredis

app_props = {
    "title": "Mapa Manage",
    "description": "Mapa Manage",
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
    container.wire(packages=[manage])
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
        #     application_name="MANAGE",
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
    application.include_router(ping_router, prefix="/api/manage/ping", tags=["ping"])
    application.include_router(role_router, prefix="/api/manage/role", tags=["role"])
    application.include_router(user_router, prefix="/api/manage/user", tags=["user"])
    application.include_router(
        role_user_router, prefix="/api/manage/role_user", tags=["role_user"]
    )
    application.include_router(
        role_api_scope_router,
        prefix="/api/manage/role_api_scope",
        tags=["role_api_scope"],
    )
    application.include_router(
        profile_adaptor_router,
        prefix="/api/manage/profile_adaptor",
        tags=["profile_adaptor"],
    )
    application.include_router(
        client_router, prefix="/api/manage/client", tags=["client"]
    )
    application.include_router(api_router, prefix="/api/manage/api", tags=["api"])
    application.include_router(
        client_api_router, prefix="/api/manage/client_api", tags=["client_api"]
    )
    application.include_router(
        api_scope_router, prefix="/api/manage/api_scope", tags=["api_scope"]
    )
    application.include_router(
        client_api_scope_router,
        prefix="/api/manage/client_api_scope",
        tags=["client_api_scope"],
    )
    application.include_router(
        invitation_router, prefix="/api/manage/invitation", tags=["invitation"]
    )
    application.include_router(
        tenant_router, prefix="/api/manage/tenant", tags=["tenant"]
    )
    application.include_router(
        organization_router, prefix="/api/manage/organization", tags=["organization"]
    )
    application.include_router(
        ldap_server_router, prefix="/api/manage/ldap_server", tags=["ldap_server"]
    )
    application.include_router(
        organization_user_router,
        prefix="/api/manage/organization_user",
        tags=["organization_user"],
    )
    application.include_router(
        organization_type_router,
        prefix="/api/manage/organization_type",
        tags=["organization_type"],
    )
    application.include_router(
        organization_role_router,
        prefix="/api/manage/organization_role",
        tags=["organization_role"],
    )
    application.include_router(
        organization_client_router,
        prefix="/api/manage/organization_client",
        tags=["organization_client"],
    )
    application.include_router(
        user_variable_type_router,
        prefix="/api/manage/user_variable_type",
        tags=["user_variable_type"],
    )


    migration = Migration(
        str(pathlib.Path(__file__).parent.parent / "migrations"), container.config.alembic()["url"]
    )
    migration.upgrade_migrations()

    # Check redirect url
    name_list = ["manage", "workspace", "application"]
    domain = container.config.domain()
    if "localhost" not in domain:
        check_redirect_uris(container.config.alembic()["url"], name_list, domain)

    return application
