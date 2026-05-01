from typing import List, Type, Optional
from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from messaging.room.entity import RoomEntity, RoomUserEntity
from messaging.room.repository import RoomRepository
from messaging.room.model import Room, CreateRoom, UpdateRoom
from sqlalchemy import insert, text

class RoomService(BaseEntityService[RoomRepository, Room, CreateRoom, UpdateRoom, UpdateRoom]):
    def __init__(self, async_db: AsyncDatabase, message_service: Optional['MessageService'] = None) -> None:
        super().__init__(async_db, RoomRepository, Room)
        self._async_db = async_db
        self._message_service = message_service

    async def add_user(self, room_id: UUID, user_id: UUID, tenant_id: str | None = None) -> bool:
        """Adds a user to a room"""
        async with self._async_db.session() as session:
            t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
            await session.execute(text(f"set app.tenant_id='{t_id}'"))
            
            stmt = insert(RoomUserEntity).values(
                room_id=room_id,
                user_id=user_id,
                tenant_id=t_id
            )
            await session.execute(stmt)
            await session.commit()
            return True

    async def remove_user(self, room_id: UUID, user_id: UUID, tenant_id: str | None = None) -> bool:
        """Removes a user from a room"""
        from sqlalchemy import delete
        async with self._async_db.session() as session:
            t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
            await session.execute(text(f"set app.tenant_id='{t_id}'"))
            
            stmt = delete(RoomUserEntity).where(
                RoomUserEntity.room_id == room_id,
                RoomUserEntity.user_id == user_id
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def get_user_rooms(self, user_id: UUID, tenant_id: str | None = None) -> List[Room]:
        """Gets all rooms (groups and DMs) a user belongs to or has conversed with"""
        async with self._async_db.session() as session:
            t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
            nil_id = "00000000-0000-0000-0000-000000000000"
            await session.execute(text(f"set app.tenant_id='{t_id}'"))
            
            # 1. Fetch Group Rooms
            from sqlalchemy import select, or_, and_
            from sqlalchemy.orm import selectinload
            from messaging.room.entity import RoomUserEntity
            
            group_stmt = (
                select(RoomEntity)
                .options(selectinload(RoomEntity.users))
                .join(RoomUserEntity, RoomEntity.id == RoomUserEntity.room_id)
                .where(RoomUserEntity.user_id == user_id)
            )
            result = await session.execute(group_stmt)
            rooms = list(result.scalars().all())
            
            # 2. Fetch Recent DM partners with names and photos
            dm_stmt = text("""
                SELECT DISTINCT partner_id, u.name, u.surname, u.picture FROM (
                    SELECT receiver_id as partner_id FROM messaging.message 
                    WHERE sender_id = :user_id AND receiver_id IS NOT NULL
                    UNION
                    SELECT sender_id as partner_id FROM messaging.message 
                    WHERE receiver_id = :user_id AND room_id IS NULL
                ) x
                LEFT JOIN manage."user" u ON x.partner_id = u.id
            """)
            dm_result = await session.execute(dm_stmt, {"user_id": user_id})
            partners = dm_result.fetchall()
            
            # 3. Merge and return
            final_rooms = []
            for r in rooms:
                final_rooms.append(Room.model_validate(r))
            
            # Add Virtual Rooms for DMs
            from datetime import datetime
            for p in partners:
                p_id, p_name, p_surname, p_foto = p
                if any(str(r.id) == str(p_id) for r in final_rooms): continue
                
                name = f"{p_name} {p_surname}" if p_name else f"User {str(p_id)[:8]}"
                final_rooms.append(Room(
                    id=p_id,
                    name=name,
                    foto=p_foto,
                    created_at=datetime.now(),
                    is_dm=True,
                    users=[],
                    tenant_id=None,
                    creator_user_id=None,
                    updater_user_id=None,
                    updated_at=None
                ))
            
            return final_rooms

    async def delete_room(self, room_id: UUID, tenant_id: str | None = None) -> bool:
        """Deletes a room, its members, and its message history"""
        await self.clear_room_history(room_id, tenant_id)
        
        from sqlalchemy import delete
        async with self._async_db.session() as session:
            t_id = tenant_id if tenant_id and tenant_id not in ('default', 'None', 'undefined') else "00000000-0000-0000-0000-000000000000"
            await session.execute(text(f"set app.tenant_id='{t_id}'"))
            
            # 1. Delete room members first to satisfy foreign key constraint
            await session.execute(delete(RoomUserEntity).where(RoomUserEntity.room_id == room_id))
            await session.commit()
        
        return await self.delete(room_id, tenant_id)

    async def clear_room_history(self, room_id: UUID, tenant_id: str | None = None) -> bool:
        """Clears message history of a room but keeps the room and members"""
        if self._message_service:
            await self._message_service.delete_room_history(room_id, tenant_id)
            return True
        return False
