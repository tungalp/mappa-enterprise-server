import mock_app
import os
from mapa.security import OAuth2IdTokenBackend
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from mock_app.config.app_container import AppContainer
from mock_app.mock.parsel_router import router as parsel_router
from mock_app.mock.any_router import router as any_router
from mapa.log.elk_middleware import ElkMiddleware
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

app_props = {
    "title": "Mapa Mock",
    "description": "Mapa Mock",
    "version": "0.0.1",
    "terms_of_service": "http://mapa.com.tr/terms/",
    "contact": {
        "name": "Admin",
        "url": "http://mapa.com.tr/contact/",
        "email": "admin@mapa.com.tr",
    },
    "license_info": {
        "name": "Mapa Commercial Licenze",
        "url": "https://mapa.com.tr/licenses/mapa.html"
    },
    "root_path": ""
}


def create_application():
    """FastAPI uygulamasını oluşturur"""

    # Konteyner
    container = AppContainer()
    container.wire(packages=[mock_app])
    # Elastic-apm
    apm = make_apm_client({
        'SERVICE_NAME': container.config.apm.service_name(),
        'SECRET_TOKEN': container.config.apm.secret_token(),
        'SERVER_URL': container.config.apm.server_url(),
        'ENVIRONMENT' : container.config.apm.environment()
    })

    middleware = [        
        # Middleware(ElasticAPM, client=apm),
        # Middleware(ElkMiddleware, application_name='MOCK_APP', host=container.config.elk.host(), port=container.config.elk.port(), env= os.environ.get("MAPA_ENV")),
        Middleware(AuthenticationMiddleware, backend=OAuth2IdTokenBackend(
            jwks_uri=container.config.oidc()["jwks_uri"]
        )),
    ]
    # Ana uygulama nesnesi
    application = FastAPI(**app_props, middleware=middleware)
    application.container = container  # type: ignore

    # Routes
    application.include_router(
        parsel_router, prefix="/parsel", tags=["mock_parsel"])
    application.include_router(
        any_router, prefix="/any", tags=["mock_any"])
    

    return application
