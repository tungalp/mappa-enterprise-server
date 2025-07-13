import asyncio
import application as Application
import os
import pathlib
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from mapa.security import OAuth2IdTokenBackend
from application.config.app_container import ApplicationContainer
from application.apps.router import router as app_router
from application.content_page.router import router as content_page_router
from application.content_page_template.router import (
    router as content_page_template_router,
)
from mapa.log.elk_middleware import ElkMiddleware

from mapa.alembic.migration import Migration
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

app_props = {
    "title": "Mapa Application",
    "description": "Mapa Application",
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
async def lifespan(application: FastAPI):
    # Startup
    async def worker():
        while True:
            try:
                await application.container.service_messenger().publish_pending_events()
            except Exception as e:
                print(f"Outbox worker error: {e}")
            await asyncio.sleep(5)
    
    task = asyncio.create_task(worker())
    yield
    # Shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


def create_application():
    """FastAPI uygulamasını oluşturur"""

    # Konteyner
    container = ApplicationContainer()
    container.wire(packages=[Application])
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
        #     application_name="APPLICATION",
        #     host=container.config.elk.host(),
        #     port=container.config.elk.port(),
        #     env=os.environ.get("MAPA_ENV"),
        #     redact_fields=sanitize_list,
        #     excluded_paths=ignore_urls,
        # ),
    ]

    # Ana uygulama nesnesi
    application = FastAPI(**app_props, middleware=middleware, redirect_slashes=False, lifespan=lifespan)
    application.container = container  # type: ignore

    application.apm_client = apm  # type: ignore
    
    # Routes
    application.include_router(app_router, prefix="/api/application/app", tags=["app"])
    application.include_router(
        content_page_router,
        prefix="/api/application/content_page",
        tags=["content_page"],
    )
    application.include_router(
        content_page_template_router,
        prefix="/api/application/content_page_template",
        tags=["content_page_template"],
    )

    migration = Migration(
        str(pathlib.Path(__file__).parent.parent / "migrations"), container.config.alembic()["url"]
    )
    migration.upgrade_migrations()

    return application
