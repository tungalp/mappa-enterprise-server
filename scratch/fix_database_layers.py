import asyncio
from sqlalchemy import text
from mapa.core.data.async_db import AsyncDatabase

async def fix_layers():
    db = AsyncDatabase("postgresql+asyncpg://postgres:postgres@postgres:5432/mapa_test")
    async with db.session() as session:
        # Check current layer records for this map
        query = text("""
            SELECT l.id, l.name, l.url_path 
            FROM desktop_mobile.layer l
            JOIN desktop_mobile.map_layer ml ON l.id = ml.layer_id
            WHERE ml.map_id = '8d66221d-d90b-4804-9200-82b6157b7543'
              AND l.type = '.gdb.zip'
        """)
        res = await session.execute(query)
        rows = res.fetchall()
        print(f"Found {len(rows)} GDB layers linked to the map.")
        
        # We will prepend 'layers/9f1159f4-4b01-4b68-9bbe-8deeacd3db60/sheet_5349_1.gdb.zip'
        # to all GDB layers starting with '|layername='
        count = 0
        for r in rows:
            layer_id = r[0]
            url_path = r[2]
            if url_path and url_path.startswith("|layername="):
                new_path = f"layers/9f1159f4-4b01-4b68-9bbe-8deeacd3db60/sheet_5349_1.gdb.zip{url_path}"
                update_query = text("""
                    UPDATE desktop_mobile.layer
                    SET url_path = :new_path, bucket = 'desktop-mobile'
                    WHERE id = :layer_id
                """)
                await session.execute(update_query, {"new_path": new_path, "layer_id": layer_id})
                count += 1
                
        await session.commit()
        print(f"Successfully repaired {count} layer paths in the database!")

if __name__ == "__main__":
    asyncio.run(fix_layers())
