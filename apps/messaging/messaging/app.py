import asyncio
import os
import pathlib
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from mapa.security import OAuth2IdTokenBackend
from messaging.config.app_container import MessagingContainer
from messaging.room.router import router as room_router
from messaging.message.router import router as message_router
from mapa.alembic.migration import Migration

app_props = {
    "title": "Mapa Messaging Service",
    "description": "Real-time Chat and GIS Signals",
    "version": "0.1.0",
}

@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup: Background worker (Outbox + Read Receipts)
    async def background_worker():
        while True:
            try:
                # Outbox
                await application.container.service_messenger().publish_pending_events()
                # Read Receipts
                await application.container.message_package.message_service().flush_read_receipts()
            except Exception as e:
                print(f"Background worker error: {e}")
            await asyncio.sleep(5)
    
    # Startup MQTT Processor task
    mqtt_processor = application.container.mqtt_processor()
    await mqtt_processor.start()
    
    task_worker = asyncio.create_task(background_worker())
    
    yield
    
    # Shutdown
    await mqtt_processor.stop()
    task_worker.cancel()
    try:
        await task_worker
    except asyncio.CancelledError:
        pass

def create_application():
    container = MessagingContainer()
    container.wire(packages=["messaging"])
    
    middleware = [
        Middleware(
            AuthenticationMiddleware,
            backend=OAuth2IdTokenBackend(jwks_uri=container.config.oidc()["jwks_uri"]),
        ),
    ]

    application = FastAPI(**app_props, middleware=middleware, lifespan=lifespan)
    application.container = container  # type: ignore

    # Routes
    application.include_router(room_router, prefix="/api/messaging/rooms", tags=["rooms"])
    application.include_router(message_router, prefix="/api/messaging/messages", tags=["messages"])

    # Migrations
    migration = Migration(
        str(pathlib.Path(__file__).parent.parent / "migrations"), 
        container.config.alembic()["url"]
    )
    migration.upgrade_migrations()

    return application
