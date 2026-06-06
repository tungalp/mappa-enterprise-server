from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Query
from dependency_injector.wiring import inject, Provide
from messaging.config.app_container import MessagingContainer
from messaging.message.model import Message
from messaging.message.service import MessageService
from messaging.message.minio_service import MinioService
from mapa.security.authentication_backend import parse_token_user_and_tenant
import uuid

router = APIRouter()

@router.get("/room/{room_id}", response_model=List[Message])
@inject
async def get_room_messages(
    request: Request,
    room_id: UUID,
    before: Optional[UUID] = Query(None),
    limit: int = Query(50, le=100),
    message_service: MessageService = Depends(Provide[MessagingContainer.message_package.message_service])
):
    _, tenant_id = parse_token_user_and_tenant(request)

    return await message_service.get_room_history(room_id, before, limit, tenant_id)

@router.get("/dm/{other_user_id}", response_model=List[Message])
@inject
async def get_dm_messages(
    request: Request,
    other_user_id: UUID,
    before: Optional[UUID] = Query(None),
    limit: int = Query(50, le=100),
    message_service: MessageService = Depends(Provide[MessagingContainer.message_package.message_service])
):
    user_id, tenant_id = parse_token_user_and_tenant(request)

    if user_id:
        return await message_service.get_dm_history(UUID(str(user_id)), other_user_id, before, limit, tenant_id)
    
    return []

@router.post("/{message_id}/read")
@inject
async def mark_read(
    request: Request,
    message_id: UUID,
    message_service: MessageService = Depends(Provide[MessagingContainer.message_package.message_service])
):
    user_id, tenant_id = parse_token_user_and_tenant(request)
    
    if user_id:
        await message_service.mark_as_read(message_id, UUID(user_id), tenant_id)
    return {"status": "ok"}

@router.post("/upload-url")
@inject
async def get_upload_url(
    filename: str,
    minio_service: MinioService = Depends(Provide[MessagingContainer.minio_service])
):
    """Generates a unique object name and pre-signed PUT URL"""
    object_name = f"{uuid.uuid4()}-{filename}"
    url = minio_service.get_presigned_upload_url(object_name)
    return {"url": url, "object_name": object_name}

@router.get("/download-url/{object_name}")
@inject
async def get_download_url(
    object_name: str,
    minio_service: MinioService = Depends(Provide[MessagingContainer.minio_service])
):
    url = minio_service.get_presigned_download_url(object_name)
    return {"url": url}

@router.delete("/dm/{other_user_id}")
@inject
async def delete_dm_history(
    request: Request,
    other_user_id: UUID,
    message_service: MessageService = Depends(Provide[MessagingContainer.message_package.message_service])
):
    user_id, tenant_id = parse_token_user_and_tenant(request)

    if not user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    await message_service.delete_dm_history(UUID(str(user_id)), other_user_id, tenant_id)
    return {"success": True}

@router.delete("/{message_id}")
@inject
async def delete_message(
    request: Request,
    message_id: UUID,
    message_service: MessageService = Depends(Provide[MessagingContainer.message_package.message_service])
):
    user_id, tenant_id = parse_token_user_and_tenant(request)

    if not user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    await message_service.delete_message(message_id, UUID(str(user_id)), tenant_id)
    return {"success": True}

