import asyncio
import sys
import uuid
import os

# Set PYTHONPATH programmatically
sys.path.insert(0, "/workspace")
sys.path.insert(0, "/workspace/apps/desktop_mobile")
sys.path.insert(0, "/workspace/libs/core")

from desktop_mobile.config.app_container import AppContainer
from desktop_mobile.models.entities import MapEntity
from sqlalchemy import select

async def rewrite_all():
    # Setup Container
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
    
    map_service = container.map_service()
    layer_service = container.layer_service()
    
    async with map_service.repo._db.session() as session:
        res = await session.execute(select(MapEntity))
        maps = res.scalars().all()
        map_ids = [m.id for m in maps]
        
    print(f"Found {len(map_ids)} map projects in database.")
    for map_id in map_ids:
        print(f"\n--- Rewriting project for Map ID: {map_id} ---")
        try:
            await layer_service._rewrite_associated_map_project(map_id)
            
            # Print updated initial_bounds
            async with map_service.repo._db.session() as session:
                res = await session.execute(select(MapEntity).where(MapEntity.id == map_id))
                db_map = res.scalars().first()
                if db_map:
                    print(f"Resulting initial_bounds: {db_map.initial_bounds}")
        except Exception as e:
            print(f"Failed for map {map_id}: {e}")

if __name__ == "__main__":
    asyncio.run(rewrite_all())
