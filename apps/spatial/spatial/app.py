import pathlib
import spatial
from mapa.alembic.migration import Migration

from mapa.security import OAuth2IdTokenBackend
from fastapi import FastAPI
from spatial.base_layer.router import router as base_layer_router
from spatial.bookmark.router import router as bookmark_router
from spatial.config.app_container import AppContainer
from spatial.connection.router import router as connection_router
from spatial.definition.router import router as definition_router
from spatial.hook.router import router as hook_router
from spatial.layer.router import router as layer_router
from spatial.layer_definition.router import router as layer_definition_router
from spatial.layer_hook.router import router as layer_hook_router
from spatial.map.router import router as map_router
from spatial.map_base_layer.router import router as map_base_layer_router
from spatial.map_layer.router import router as map_layer_router
from spatial.namespace.router import router as namespace_router
from spatial.reference.router import router as reference_router
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
import asyncio
import os
from mapa.log.elk_middleware import ElkMiddleware

app_props = {
    "title": "Mapa Spatial",
    "description": "Mapa Spatial",
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
    container.wire(packages=[spatial])
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
        #     application_name="SPATIAL",
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
    application.include_router(
        namespace_router, prefix="/api/spatial/namespace", tags=["namespace"]
    )

    application.include_router(map_router, prefix="/api/spatial/map", tags=["map"])

    application.include_router(
        connection_router, prefix="/api/spatial/connection", tags=["connection"]
    )

    application.include_router(
        layer_router, prefix="/api/spatial/layer", tags=["layer"]
    )

    application.include_router(
        definition_router, prefix="/api/spatial/definition", tags=["definition"]
    )

    application.include_router(
        layer_definition_router,
        prefix="/api/spatial/layer_definition",
        tags=["layer_definition"],
    )

    application.include_router(
        map_layer_router, prefix="/api/spatial/map_layer", tags=["map_layer"]
    )

    application.include_router(
        reference_router, prefix="/api/spatial/reference", tags=["reference"]
    )

    application.include_router(
        bookmark_router, prefix="/api/spatial/bookmark", tags=["bookmark"]
    )

    application.include_router(
        map_base_layer_router,
        prefix="/api/spatial/map_base_layer",
        tags=["map_base_layer"],
    )

    application.include_router(
        base_layer_router, prefix="/api/spatial/base_layer", tags=["base_layer"]
    )

    application.include_router(hook_router, prefix="/api/spatial/hook", tags=["hook"])

    application.include_router(
        layer_hook_router, prefix="/api/spatial/layer_hook", tags=["layer_hook"]
    )

    migration = Migration(
        str(pathlib.Path(__file__).parent.parent / "migrations"), container.config.alembic()["url"]
    )
    migration.upgrade_migrations()


    return application
