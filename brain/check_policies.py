import asyncio
from uuid import UUID
from sqlalchemy import text
from mapa.core.data.async_db import AsyncDatabase
import os

async def check_rls():
    # Attempt to connect using the same logic as the app
    # We need to find the database URL
    db_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres" # Adjust if needed
    
    # Actually, let's just use the existing AsyncDatabase if we can find where it's configured
    # For now, let's try to inspect the policies via SQL
    db = AsyncDatabase(db_url)
    
    async with db.session() as session:
        print("--- Checking RLS Policies ---")
        res = await session.execute(text("""
            SELECT schemaname, tablename, policyname, roles, cmd, qual 
            FROM pg_policies 
            WHERE schemaname = 'messaging';
        """))
        for row in res:
            print(f"Policy: {row.policyname} on {row.tablename}")
            print(f"  Qual: {row.qual}")
            print(f"  Roles: {row.roles}")
            print("-" * 20)
            
        print("\n--- Checking Current Session Variables ---")
        try:
            res = await session.execute(text("SHOW app.tenant_id;"))
            print(f"app.tenant_id: {res.scalar()}")
        except Exception as e:
            print(f"Error showing app.tenant_id: {e}")

if __name__ == "__main__":
    asyncio.run(check_rls())
