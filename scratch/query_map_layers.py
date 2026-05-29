import asyncio
from sqlalchemy import select, text
from mapa.core.data.async_db import AsyncDatabase

async def query_layers():
    db = AsyncDatabase("postgresql+asyncpg://postgres:postgres@postgres:5432/mapa_test")
    async with db.session() as session:
        query = text("""
            SELECT id, name, type, url_path, bucket 
            FROM desktop_mobile.layer
        """)
        res = await session.execute(query)
        rows = res.fetchall()
        print(f"Total layers linked: {len(rows)}")
        for r in rows:
            print(f"ID: {r[0]} | Name: {r[1]} | Type: {r[2]} | UrlPath: {r[3]} | Bucket: {r[4]}")

asyncio.run(query_layers())
