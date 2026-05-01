import asyncio
from sqlalchemy import text
from mapa.core.data.async_db import AsyncDatabase

async def fix_database_policies():
    # Update this to your actual database URL
    db_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    db = AsyncDatabase(db_url)
    
    tables = [
        "messaging.message",
        "messaging.room",
        "messaging.room_users"
    ]
    
    nil_id = "00000000-0000-0000-0000-000000000000"
    
    async with db.session() as session:
        print("--- Fixing RLS Policies ---")
        for table in tables:
            policy_name = f"{table.split('.')[-1]}_isolation_policy"
            print(f"Updating policy for {table}...")
            
            # 1. Drop old policy if exists
            await session.execute(text(f"DROP POLICY IF EXISTS {policy_name} ON {table}"))
            
            # 2. Create new 'Safe' policy
            # Note the use of current_setting(..., true) which prevents crashing if variable is missing
            new_policy = f"""
                CREATE POLICY {policy_name} ON {table}
                USING (
                    (current_setting('app.tenant_id', true) = tenant_id::text) 
                    OR (tenant_id::text = '{nil_id}') 
                    OR (tenant_id IS NULL)
                )
            """
            await session.execute(text(new_policy))
            print(f"  Successfully updated {table}")
            
        await session.commit()
        print("\nDatabase policies have been repaired!")

if __name__ == "__main__":
    asyncio.run(fix_database_policies())
