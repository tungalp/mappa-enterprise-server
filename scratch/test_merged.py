import asyncio
import uuid
import sys
import os

# Set MAPA_ENV to DEVELOPMENT so it connects to mapa_test database
os.environ["MAPA_ENV"] = "DEVELOPMENT"

# Add apps/desktop_mobile to path
sys.path.insert(0, '/workspace/apps/desktop_mobile')

from desktop_mobile.config.app_container import AppContainer

async def main():
    container = AppContainer()
    container.init_resources()
    map_service = container.map_service()
    
    map_id = uuid.UUID('8d66221d-d90b-4804-9200-82b6157b7543')
    res = await map_service.get_map_merged(map_id)
    
    print('Total layers:', len(res.layers))
    print('Layers with non-null groups:')
    count = 0
    for l in res.layers:
        if l.group:
            print(f"  Name: {l.name} | Group: {l.group}")
            count += 1
    print('Total grouped layers:', count)

if __name__ == '__main__':
    asyncio.run(main())
