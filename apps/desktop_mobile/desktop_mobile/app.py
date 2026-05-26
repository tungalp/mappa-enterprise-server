import pathlib
import desktop_mobile
from mapa.alembic.migration import Migration
from mapa.security import OAuth2IdTokenBackend
from fastapi import FastAPI
from desktop_mobile.config.app_container import AppContainer
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import AuthCredentials, UnauthenticatedUser
from elasticapm.contrib.starlette import make_apm_client
import asyncio
import os

from desktop_mobile.api.apikey_router import router as apikey_router
from desktop_mobile.api.collection_router import router as collection_router
from desktop_mobile.api.map_router import router as map_router
from desktop_mobile.api.layer_router import router as layer_router

app_props = {
    "title": "Mapa Desktop & Mobile Store",
    "description": "Mapa QGIS Desktop Add-in and Mobile Client Synchronized GIS Store",
    "version": "1.0.0",
    "terms_of_service": "http://mapa.com.tr/terms/",
    "contact": {
        "name": "Admin",
        "url": "http://mapa.com.tr/contact/",
        "email": "admin@mapa.com.tr",
    },
    "license_info": {
        "name": "Mapa Commercial License",
        "url": "https://mapa.com.tr/licenses/mapa.html",
    },
    "root_path": "",
}

class DesktopOAuth2Backend(OAuth2IdTokenBackend):
    async def authenticate(self, conn):
        auth_header = conn.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            if token.startswith("pk_") or token.count(".") != 2:
                return AuthCredentials(), UnauthenticatedUser()
            
            # Attempt to decode locally as an HS256 JWT token
            try:
                from desktop_mobile.services.auth import decode_jwt
                from mapa.security.authentication_backend import AuthenticatedUser
                payload = decode_jwt(token)
                # Token is a valid local HS256 JWT
                return AuthCredentials(scopes=[]), AuthenticatedUser(payload["sub"], payload)
            except Exception:
                # Not a valid local JWT, fallback to super OIDC authenticate
                pass
                
        return await super().authenticate(conn)

def create_application():
    """FastAPI uygulamasını oluşturur"""
    # Container setup
    container = AppContainer()
    container.wire(
        packages=["desktop_mobile"],
        modules=[
            "desktop_mobile.services.auth",
            "desktop_mobile.api.apikey_router",
            "desktop_mobile.api.collection_router",
            "desktop_mobile.api.map_router",
            "desktop_mobile.api.layer_router",
        ]
    )
    
    sanitize_raw = container.config.apm.sanitize_field_names()
    sanitize_list = [item.strip() for item in sanitize_raw.split(",") if item.strip()]  
    ignore_urls = ["/health*"]
    
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
            backend=DesktopOAuth2Backend(jwks_uri=container.config.oidc()["jwks_uri"]),
        ),
    ]
    
    application = FastAPI(**app_props, middleware=middleware, redirect_slashes=False)
    application.container = container
    application.apm_client = apm

    # Mount routers
    application.include_router(apikey_router, prefix="/api/desktop-mobile/api_keys", tags=["API Keys"])
    application.include_router(collection_router, prefix="/api/desktop-mobile/collections", tags=["Collections"])
    application.include_router(map_router, prefix="/api/desktop-mobile/maps", tags=["Maps"])
    application.include_router(layer_router, prefix="/api/desktop-mobile/layers", tags=["Layers"])
    
    # Auto Database Alembic migrations upgrade on startup
    migration_path = str(pathlib.Path(__file__).parent.parent / "migrations")
    if os.path.exists(migration_path):
        migration = Migration(
            migration_path, container.config.alembic()["url"]
        )
        try:
            migration.upgrade_migrations()
        except Exception as e:
            print(f"[Alembic] Auto migration failed (might be fine if first run or database is offline in test): {e}")
            
    return application
