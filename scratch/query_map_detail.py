import asyncio
import uuid
from sqlalchemy import select, text
from mapa.core.data.async_db import AsyncDatabase

async def query_map_detail():
    db = AsyncDatabase("postgresql+asyncpg://postgres:postgres@postgres:5432/mapa_test")
    map_id = uuid.UUID("8d66221d-d90b-4804-9200-82b6157b7543")
    async with db.session() as session:
        # Get map info
        q_map = text("SELECT id, name, project_file_url FROM desktop_mobile.map WHERE id = :map_id")
        res_map = await session.execute(q_map, {"map_id": map_id})
        row_map = res_map.first()
        if row_map:
            print(f"Map ID: {row_map[0]} | Name: {row_map[1]} | ProjectUrl: {row_map[2]}")
        else:
            print(f"Map {map_id} not found in database!")
            return

        # Get linked layers
        q_layers = text("""
            SELECT l.id, l.name, l.type, l.url_path, l.bucket 
            FROM desktop_mobile.layer l
            JOIN desktop_mobile.map_layer ml ON l.id = ml.layer_id
            WHERE ml.map_id = :map_id
        """)
        res_layers = await session.execute(q_layers, {"map_id": map_id})
        rows = res_layers.fetchall()
        print(f"\nTotal layers linked to map: {len(rows)}")
        for r in rows:
            print(f"  ID: {r[0]} | Name: {r[1]} | Type: {r[2]} | UrlPath: {r[3]} | Bucket: {r[4]}")

asyncio.run(query_map_detail())
