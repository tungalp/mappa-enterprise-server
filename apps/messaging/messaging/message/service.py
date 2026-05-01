from typing import List, Optional
from uuid import UUID
from redis.asyncio import Redis
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from messaging.message.entity import MessageEntity, MessageFileEntity
from messaging.message.repository import MessageRepository
from messaging.message.model import Message, CreateMessage
from sqlalchemy import insert, text

class MessageService(BaseEntityService[MessageRepository, Message, CreateMessage, CreateMessage, CreateMessage]):
    def __init__(self, async_db: AsyncDatabase, redis: Redis, minio_service: Optional['MinioService'] = None) -> None:
        super().__init__(async_db, MessageRepository, Message)
        self._async_db = async_db
        self._redis = redis
        self._minio_service = minio_service

    async def get_room_history(
        self,
        room_id: UUID,
        last_seen_id: Optional[UUID] = None,
        limit: int = 50,
        tenant_id: str | None = None
    ) -> List[Message]:
        db_objs = await self.repo.keyset_paginate_room(room_id, last_seen_id, limit, tenant_id)
        return [self.model_type.model_validate(obj) for obj in db_objs]

    async def get_dm_history(
        self,
        user_a: UUID,
        user_b: UUID,
        last_seen_id: Optional[UUID] = None,
        limit: int = 50,
        tenant_id: str | None = None
    ) -> List[Message]:
        db_objs = await self.repo.keyset_paginate_dm(user_a, user_b, last_seen_id, limit, tenant_id)
        return [self.model_type.model_validate(obj) for obj in db_objs]

    async def create(self, input_obj: CreateMessage, tenant_id: str | None = None, user_id: str | None = None) -> Message:
        """Persists a message and its file attachments"""
        async with self._async_db.session() as session:
            if tenant_id:
                await session.execute(text(f"set app.tenant_id='{tenant_id}'"))
            
            # 1. Create message
            msg_dict = input_obj.model_dump(exclude={"file_urls"})
            db_msg = MessageEntity(**msg_dict)
            db_msg.tenant_id = tenant_id
            db_msg.sender_id = UUID(user_id) if user_id else None
            session.add(db_msg)
            await session.flush() # Get ID
            
            # 2. Create file attachments
            if input_obj.file_urls:
                for url in input_obj.file_urls:
                    file_obj = MessageFileEntity(
                        message_id=db_msg.id,
                        file_url=url,
                        tenant_id=tenant_id
                    )
                    session.add(file_obj)
            
            await session.commit()
            return self.model_type.model_validate(self.repo.dict(db_msg))

    async def mark_as_read(self, message_id: UUID, user_id: UUID, tenant_id: str | None = None):
        """Buffer read receipt in Redis"""
        key = f"read_buffer:{tenant_id}:{message_id}"
        await self._redis.sadd(key, str(user_id))
        # Set expiry to ensure it doesn't leak if worker dies, 
        # but worker should flush it every few seconds
        await self._redis.expire(key, 60) 

    async def flush_read_receipts(self):
        """Flushes buffered read receipts from Redis to PostgreSQL"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Scan for all read buffers
        # Pattern: read_buffer:{tenant_id}:{message_id}
        cursor = 0
        while True:
            cursor, keys = await self._redis.scan(cursor, match="read_buffer:*", count=100)
            for key in keys:
                try:
                    parts = key.split(":")
                    if len(parts) < 3: continue
                    tenant_id = parts[1] if parts[1] != "None" else None
                    message_id = UUID(parts[2])
                    
                    user_ids = await self._redis.smembers(key)
                    if not user_ids: continue
                    
                    await self._update_message_read_status(message_id, user_ids, tenant_id)
                    await self._redis.delete(key)
                except Exception as e:
                    logger.error(f"Error flushing read receipt for key {key}: {e}")
            
            if cursor == 0:
                break

    async def _update_message_read_status(self, message_id: UUID, user_ids: List[str], tenant_id: str | None):
        from datetime import datetime
        async with self._async_db.session() as session:
            if tenant_id:
                await session.execute(text(f"set app.tenant_id='{tenant_id}'"))
            
            # Simple logic: update read1_at if sender/receiver match, or read2_at for others
            # For now, let's just set read1_at to now() for simplicity as a proof of concept
            from sqlalchemy import update
            stmt = update(MessageEntity).where(MessageEntity.id == message_id).values(
                read1_at=datetime.now()
            )
            await session.execute(stmt)
            await session.commit()

    async def delete_room_history(self, room_id: UUID, tenant_id: str | None = None):
        """Deletes all messages and files in a room"""
        if self._minio_service:
            messages = await self.repo.keyset_paginate_room(room_id, limit=10000, tenant_id=tenant_id)
            for msg in messages:
                for file in msg.files:
                    # Extract object name from URL (usually last part after /)
                    object_name = file.file_url.split("/")[-1]
                    self._minio_service.delete_object(object_name)
        
        await self.repo.delete_room_messages(room_id, tenant_id)

    async def delete_dm_history(self, user_a: UUID, user_b: UUID, tenant_id: str | None = None):
        """Deletes all messages and files between two users"""
        if self._minio_service:
            messages = await self.repo.keyset_paginate_dm(user_a, user_b, limit=10000, tenant_id=tenant_id)
            for msg in messages:
                for file in msg.files:
                    object_name = file.file_url.split("/")[-1]
                    self._minio_service.delete_object(object_name)
        
        await self.repo.delete_dm_messages(user_a, user_b, tenant_id)
