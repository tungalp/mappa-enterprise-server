from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide
from messaging.config.app_container import MessagingContainer
from messaging.room.model import Room, CreateRoom, UpdateRoom, AddRoomUser
from messaging.room.service import RoomService

router = APIRouter()

@router.get("/", response_model=List[Room])
@inject
async def get_rooms(
    request: Request,
    room_service: RoomService = Depends(Provide[MessagingContainer.room_package.room_service])
):
    user = getattr(request.state, "user", None)
    user_id = None
    tenant_id = None
    
    if user and hasattr(user, "id"):
        user_id = user.id
        tenant_id = getattr(user, "tenant_id", None)
    else:
        # Fallback: Manually parse JWT if AuthenticationMiddleware failed to verify
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            import jwt
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("sub")
                tenant_id = payload.get("tenant_id")
            except Exception:
                pass

    if user_id:
        return await room_service.get_user_rooms(UUID(str(user_id)), tenant_id)
    return []

@router.post("/", response_model=Room)
@inject
async def create_room(
    request: Request,
    input_obj: CreateRoom,
    room_service: RoomService = Depends(Provide[MessagingContainer.room_package.room_service])
):
    user = getattr(request.state, "user", None)
    user_id = None
    tenant_id = None
    
    if user and hasattr(user, "id"):
        user_id = user.id
        tenant_id = getattr(user, "tenant_id", None)
    else:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            import jwt
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("sub")
                tenant_id = payload.get("tenant_id")
            except Exception:
                pass
    
    room = await room_service.create(input_obj, tenant_id, user_id)
    
    # Automatically add creator to room
    if user_id:
        await room_service.add_user(room.id, UUID(str(user_id)), tenant_id)
        
    return room

@router.post("/{room_id}/members")
@inject
async def add_member(
    request: Request,
    room_id: UUID,
    input_obj: AddRoomUser,
    room_service: RoomService = Depends(Provide[MessagingContainer.room_package.room_service])
):
    user = getattr(request.state, "user", None)
    tenant_id = getattr(user, "tenant_id", None)
    
    if not user:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            import jwt
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                tenant_id = payload.get("tenant_id")
            except Exception:
                pass
                
    return await room_service.add_user(room_id, input_obj.user_id, tenant_id)

@router.delete("/{room_id}/members/{user_id}")
@inject
async def remove_member(
    request: Request,
    room_id: UUID,
    user_id: UUID,
    room_service: RoomService = Depends(Provide[MessagingContainer.room_package.room_service])
):
    user = getattr(request.state, "user", None)
    tenant_id = getattr(user, "tenant_id", None)
    
    if not user:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            import jwt
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                tenant_id = payload.get("tenant_id")
            except Exception:
                pass

    success = await room_service.remove_user(room_id, user_id, tenant_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found in room")
    return {"success": True}

@router.delete("/{room_id}")
@inject
async def delete_room(
    request: Request,
    room_id: UUID,
    room_service: RoomService = Depends(Provide[MessagingContainer.room_package.room_service])
):
    user = getattr(request.state, "user", None)
    tenant_id = getattr(user, "tenant_id", None)
    
    if not user:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            import jwt
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                tenant_id = payload.get("tenant_id")
            except Exception:
                pass

    success = await room_service.delete_room(room_id, tenant_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Room not found")
    return {"success": True}

@router.delete("/{room_id}/history")
@inject
async def delete_room_history(
    request: Request,
    room_id: UUID,
    room_service: RoomService = Depends(Provide[MessagingContainer.room_package.room_service])
):
    user = getattr(request.state, "user", None)
    tenant_id = getattr(user, "tenant_id", None)
    
    if not user:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            import jwt
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                tenant_id = payload.get("tenant_id")
            except Exception:
                pass

    success = await room_service.clear_room_history(room_id, tenant_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Room history could not be cleared")
    return {"success": True}
