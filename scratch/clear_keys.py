import asyncio
import os
os.environ["MAPA_ENV"] = "DEVELOPMENT"

from desktop_mobile.config.app_container import AppContainer
from desktop_mobile.models.entities import ApiKeyEntity, ApiKeyPermissionEntity
from sqlalchemy import delete

async def clear_keys():
    container = AppContainer()
    async with container.db().session() as session:
        await session.execute(delete(ApiKeyPermissionEntity))
        await session.execute(delete(ApiKeyEntity))
        await session.commit()
    print("Cleared all existing API Keys and permissions successfully!")

if __name__ == "__main__":
    asyncio.run(clear_keys())
