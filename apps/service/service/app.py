import asyncio
import pathlib
import service
import os
from mapa.security import OAuth2IdTokenBackend
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from service.config.app_container import AppContainer

from service.http_client.http_client import close_global_client
from service.root.router import router as root_router
from mapa.log.elk_middleware import ElkMiddleware
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import Redis
from redis import asyncio as aioredis
import yaml
from starlette.middleware.base import BaseHTTPMiddleware

app_props = {
    "title": "Mapa Service",
    "description": "Mapa Service",
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
        # WRITE → master üzerinden
        write_redis = await aioredis.from_url(
            f"redis://{redis_conf['host']}:{redis_conf['write_port']}",
            password=redis_conf["password"],
            db=redis_conf["db"],
            encoding="utf-8",
        )

        # READ → slave'ler üzerinden (HAProxy roundrobin ile)
        read_redis = await aioredis.from_url(
            f"redis://{redis_conf['host']}:{redis_conf['read_port']}",
            password=redis_conf["password"],
            db=redis_conf["db"],
            encoding="utf-8",
        )

        # Varsayılan cache Redis'i write için kullanalım
        FastAPICache.init(RedisBackend(write_redis), prefix=redis_conf["prefix"])

        print(f"write server version: {(await write_redis.info())['redis_version']}")
        print(f"read server version: {(await read_redis.info())['redis_version']}")
        # Bağlantıları uygulama durumuna ekle
        app.state.redis_write = write_redis
        app.state.redis_read = read_redis

        print("Redis bağlantıları başarılı (read & write ayrıldı)")

    except Exception as e:
        print(f"Redis bağlantı hatası: {e}")

    yield

    await write_redis.close()
    await read_redis.close()
    await close_global_client()


def create_application():
    """FastAPI uygulamasını oluşturur"""

    # Konteyner
    container = AppContainer()
    container.wire(packages=[service])
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
            "TRANSACTION_IGNORE_URLS": ignore_urls,
        }
    )

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=OAuth2IdTokenBackend(jwks_uri=container.config.oidc()["jwks_uri"]),
        ),

        # Middleware(ElasticAPM, client=apm),
        # Middleware(
        #     ElkMiddleware,
        #     application_name="SERVICE",
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
    application.include_router(root_router, prefix="", tags=["root"])



    return application
