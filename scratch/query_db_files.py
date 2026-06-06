import asyncio
from sqlalchemy import select, text
from mapa.core.data.async_db import AsyncDatabase
from messaging.message.entity import MessageFileEntity

async def main():
    from messaging.config.app_container import MessagingContainer
    container = MessagingContainer()
    container.config.from_yaml("/workspace/apps/messaging/messaging/config/config.yml")
    db = container.core.async_db()
    
    async with db.session() as session:
        # Set tenant to bypass row security
        await session.execute(text("set app.tenant_id='00000000-0000-0000-0000-000000000000'"))
        stmt = select(MessageFileEntity).limit(10)
        res = await session.execute(stmt)
        files = res.scalars().all()
        print(f"Found {len(files)} files in db")
        for f in files:
            print(f"ID: {f.id} | Message ID: {f.message_id} | File URL: {f.file_url} | File Name: {f.file_name}")

if __name__ == "__main__":
    asyncio.run(main())
