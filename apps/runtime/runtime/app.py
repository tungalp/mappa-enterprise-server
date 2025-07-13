import runtime
import os
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from runtime.config.app_container import AppContainer
from runtime.root.router import router as root_router
from mapa.log.elk_middleware import ElkMiddleware
from contextlib import asynccontextmanager

app_props = {
    "title": "Mapa Runtime",
    "description": "Mapa Runtime Service",
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    app.container.shutdown_resources()

def create_application():
    """FastAPI uygulamasını oluşturur"""

    # Konteyner
    container = AppContainer()
    container.wire(packages=[runtime])

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_methods=["*"],
            allow_headers=["*"]
        ),        
        # Middleware(AuthenticationMiddleware, backend=OAuth2IdTokenBackend(
        #     jwks_uri=container.config.oidc()["jwks_uri"]
        # )),
        Middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_methods=["*"],
            allow_headers=["*"]
        ),
        Middleware(ElkMiddleware,
                   application_name='RUNTIME',
                   host=container.config.elk.host(),
                   port=container.config.elk.port(),
                   env= os.environ.get("MAPA_ENV")),           
    ]
    # Ana uygulama nesnesi
    application = FastAPI(**app_props, middleware=middleware, lifespan=lifespan)
    application.container = container  # type: ignore

    # Routes
    application.include_router(
        root_router, prefix="", tags=["root"])
    
    return application
