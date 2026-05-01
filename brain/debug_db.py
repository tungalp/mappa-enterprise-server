import asyncio
from uuid import UUID
from sqlalchemy import select, text
from mapa.core.data.async_db import AsyncDatabase
from messaging.message.entity import MessageEntity
from messaging.config.app_config import AppConfig

async def debug_dump_messages():
    config = AppConfig()
    db = AsyncDatabase(config.db_url)
    
    print(f"Connecting to {config.db_url}...")
    
    async with db.session() as session:
        # Check if RLS is hiding things by running a raw query without setting tenant_id
        stmt = select(MessageEntity).limit(10)
        result = await session.execute(stmt)
        messages = result.scalars().all()
        
        print(f"Found {len(messages)} messages in total (no RLS set in session)")
        for m in messages:
            print(f"ID: {m.id}, Sender: {m.sender_id}, Receiver: {m.receiver_id}, Tenant: {m.tenant_id}, Msg: {m.message[:20]}")

        # Now try with a dummy tenant_id to see if they disappear
        print("\nSetting app.tenant_id to a dummy value...")
        await session.execute(text("SELECT set_config('app.tenant_id', '00000000-0000-0000-0000-000000000000', false)"))
        result = await session.execute(stmt)
        messages_rls = result.scalars().all()
        print(f"Found {len(messages_rls)} messages with RLS set")

if __name__ == "__main__":
    asyncio.run(debug_dump_messages())
