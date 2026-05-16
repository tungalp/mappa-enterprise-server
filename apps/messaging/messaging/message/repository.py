from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, text, delete, or_, and_
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from messaging.message.entity import MessageEntity, MessageFileEntity

class MessageRepository(BaseRepository[MessageEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, MessageEntity)

    async def keyset_paginate_room(
        self,
        room_id: UUID,
        last_seen_id: Optional[UUID] = None,
        limit: int = 50,
        tenant_id: str | None = None
    ) -> List[MessageEntity]:
        """High-performance keyset pagination for room messages"""
        from sqlalchemy import or_, and_
        t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
        nil_id = "00000000-0000-0000-0000-000000000000"

        from sqlalchemy.orm import selectinload
        
        stmt = (
            select(MessageEntity)
            .options(selectinload(MessageEntity.files))
            .where(
                and_(
                    MessageEntity.room_id == room_id,
                    or_(
                        MessageEntity.tenant_id == UUID(t_id),
                        MessageEntity.tenant_id == UUID(nil_id),
                        MessageEntity.tenant_id == None
                    )
                )
            )
            .order_by(MessageEntity.created_at.desc())
            .limit(limit)
        )
        
        if last_seen_id:
            # We use ID for keyset since it's monotonic or at least indexed for sorting
            # In PostgreSQL, UUID v4 is not perfectly monotonic, but we have an index on (room_id, id DESC)
            stmt = stmt.where(MessageEntity.id < last_seen_id)

        async with self._db.session() as session:
            t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
            await session.execute(text(f"set app.tenant_id='{t_id}'"))
            result = await session.execute(stmt)
            return result.scalars().all()

    async def keyset_paginate_dm(
        self,
        user_a: UUID,
        user_b: UUID,
        last_seen_id: Optional[UUID] = None,
        limit: int = 50,
        tenant_id: str | None = None
    ) -> List[MessageEntity]:
        """High-performance keyset pagination for Direct Messages"""
        # (sender=A and receiver=B) or (sender=B and receiver=A)
        from sqlalchemy import or_, and_, text
        
        t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
        nil_id = "00000000-0000-0000-0000-000000000000"

        from sqlalchemy.orm import selectinload
        
        stmt = (
            select(MessageEntity)
            .options(selectinload(MessageEntity.files))
            .where(
                and_(
                    or_(
                        and_(MessageEntity.sender_id == user_a, MessageEntity.receiver_id == user_b),
                        and_(MessageEntity.sender_id == user_b, MessageEntity.receiver_id == user_a)
                    ),
                    or_(
                        MessageEntity.tenant_id == UUID(t_id),
                        MessageEntity.tenant_id == UUID(nil_id),
                        MessageEntity.tenant_id == None
                    )
                )
            )
            .order_by(MessageEntity.created_at.desc())
            .limit(limit)
        )
        
        if last_seen_id:
            stmt = stmt.where(MessageEntity.id < last_seen_id)

        async with self._db.session() as session:
            t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
            await session.execute(text(f"set app.tenant_id='{t_id}'"))
            result = await session.execute(stmt)
            return result.scalars().all()

    async def delete_room_messages(self, room_id: UUID, tenant_id: str | None = None):
        """Deletes all messages and their file records in a room"""
        async with self._db.session() as session:
            t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
            await session.execute(text(f"set app.tenant_id='{t_id}'"))
            
            # 1. Delete associated files first to satisfy foreign key constraint
            file_stmt = delete(MessageFileEntity).where(
                MessageFileEntity.message_id.in_(
                    select(MessageEntity.id).where(MessageEntity.room_id == room_id)
                )
            )
            await session.execute(file_stmt)
            
            # 2. Delete messages
            msg_stmt = delete(MessageEntity).where(MessageEntity.room_id == room_id)
            await session.execute(msg_stmt)
            await session.commit()

    async def delete_dm_messages(self, user_a: UUID, user_b: UUID, tenant_id: str | None = None):
        """Deletes all messages and their file records between two users"""
        async with self._db.session() as session:
            t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
            await session.execute(text(f"set app.tenant_id='{t_id}'"))
            
            dm_condition = or_(
                and_(MessageEntity.sender_id == user_a, MessageEntity.receiver_id == user_b),
                and_(MessageEntity.sender_id == user_b, MessageEntity.receiver_id == user_a)
            )

            # 1. Delete associated files first
            file_stmt = delete(MessageFileEntity).where(
                MessageFileEntity.message_id.in_(
                    select(MessageEntity.id).where(dm_condition)
                )
            )
            await session.execute(file_stmt)
            
            # 2. Delete messages
            msg_stmt = delete(MessageEntity).where(dm_condition)
            await session.execute(msg_stmt)
            await session.commit()

    async def delete_message_by_id(self, message_id: UUID, tenant_id: str | None = None):
        """Deletes a single message and its file records"""
        async with self._db.session() as session:
            t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
            await session.execute(text(f"set app.tenant_id='{t_id}'"))
            
            # 1. Delete associated files first
            file_stmt = delete(MessageFileEntity).where(MessageFileEntity.message_id == message_id)
            await session.execute(file_stmt)
            
            # 2. Delete message
            msg_stmt = delete(MessageEntity).where(MessageEntity.id == message_id)
            await session.execute(msg_stmt)
            await session.commit()
