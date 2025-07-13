import pathlib
import sso
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from sso.config.app_container import AppContainer
from sso.oidc.router import router as oidc_router
from sso.ping.router import router as ping_router
from sso.auth.router import router as auth_router
from sso.tenant.router import router as tenant_router
from sso.user.router import router as user_router
from sso.client.router import router as client_router
from mapa.sso.constants import SsoConstants
from mapa.log.elk_middleware import ElkMiddleware
from mapa.alembic.migration import Migration
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
import asyncio
import os

app_props = {
    "title": "Mapa Single Sign On",
    "description": "Mapa Single Sign On",
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


def create_application():
    """FastAPI uygulamasını oluşturur"""

    # Konteyner
    container = AppContainer()
    container.init_resources()
    container.wire(packages=[sso])
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

    secret_key = container.config.session.secret()
    middleware = [
        Middleware(
            SessionMiddleware,
            secret_key=secret_key,
            session_cookie=SsoConstants.SESSION_COOKIE_NAME,
        ),
        Middleware(
            CORSMiddleware,
            allow_credentials=True,
            allow_origins=["*"],
            allow_origin_regex=".*",
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        # Middleware(ElasticAPM, client=apm),
        # Middleware(
        #     ElkMiddleware,
        #     application_name="SSO",
        #     host=container.config.elk.host(),
        #     port=container.config.elk.port(),
        #     env=os.environ.get("MAPA_ENV"),
        #     redact_fields=sanitize_list,
        #     excluded_paths=ignore_urls,
        # ),
    ]

    # Ana uygulama nesnesi
    application = FastAPI(**app_props, middleware=middleware, redirect_slashes=False)
    application.container = container  # type: ignore
    application.apm_client = apm  # type: ignore
    
    @application.on_event("shutdown")
    def application_shutdown():
        container.shutdown_resources()

    @application.on_event("startup")
    async def start_outbox_worker():
        async def worker():
            while True:
                try:
                    await container.service_messenger().publish_pending_events()
                except Exception as e:
                    print(f"Outbox worker error: {e}")
                await asyncio.sleep(5)
        asyncio.create_task(worker())
        
    # Routes
    application.include_router(ping_router, prefix="/api/sso/ping", tags=["ping"])
    application.include_router(oidc_router, prefix="/api/sso/oidc", tags=["oidc"])
    application.include_router(auth_router, prefix="/api/sso/auth", tags=["auth"])
    application.include_router(tenant_router, prefix="/api/sso/tenant", tags=["tenant"])
    application.include_router(user_router, prefix="/api/sso/user", tags=["user"])
    application.include_router(client_router, prefix="/api/sso/client", tags=["client"])

    migration = Migration(
        str(pathlib.Path(__file__).parent.parent / "migrations"), container.config.alembic()["url"]
    )
    migration.upgrade_migrations()

    return application
