from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid

from dependency_injector.wiring import Provide, inject
from mapa.core.data.query_args import QueryArgs, Filter, FilterOp
from desktop_mobile.config.app_container import AppContainer
from desktop_mobile.services.business_services import ApiKeyService, ApiKeyPermissionService
from desktop_mobile.services.auth import (
    check_permission,
    create_jwt,
    get_verified_api_key,
    ResourceAccess,
    ResourceType,
    TOKEN_EXPIRATION_MINUTES
)
from desktop_mobile.models.entities import ApiKeyEntity, ApiKeyPermissionEntity
from desktop_mobile.models.schemas import (
    ApiKeyResponse,
    ApiKeyCreate,
    ApiKeyPermissionResponse,
    ApiKeyPermissionCreate,
    TokenResponse,
    UserPrincipal
)

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
@inject
async def create_api_key(
    request: Request,
    key_data: ApiKeyCreate,
    api_key_service: ApiKeyService = Depends(Provide[AppContainer.api_key_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    """Generates a new API Key, hashes it, and returns the raw secret key ONCE."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    result = await api_key_service.generate_key(
        description=key_data.description,
        expires_at=key_data.expires_at,
        tenant_id=tenant_id,
        is_first=False
    )
    return result

@router.post("/first", status_code=status.HTTP_201_CREATED)
@inject
async def create_first_api_key(
    request: Request,
    key_data: ApiKeyCreate,
    api_key_service: ApiKeyService = Depends(Provide[AppContainer.api_key_service])
):
    """Generates the system's first API Key and automatically grants global ADMIN privileges."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    
    # Verify no keys currently exist in the database
    count = await api_key_service.count(QueryArgs(limit=1))
    if count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="First API key already exists. Use the standard endpoint with admin permissions."
        )
        
    result = await api_key_service.generate_key(
        description=key_data.description,
        expires_at=key_data.expires_at,
        tenant_id=tenant_id,
        is_first=True
    )
    return result

async def resolve_apikey_id(
    key_id_str: str,
    api_key_service: ApiKeyService,
    tenant_id: str | None
) -> uuid.UUID:
    try:
        return uuid.UUID(key_id_str)
    except ValueError:
        # Not a valid UUID, assume it's a public_lookup_id
        qa = QueryArgs(where=[Filter(field="public_lookup_id", op=FilterOp.EQUAL, value=key_id_str)])
        api_key = await api_key_service.find_one(qa, tenant_id)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API Key with lookup ID '{key_id_str}' not found"
            )
        return api_key.id

@router.delete("/{key_id}", status_code=status.HTTP_200_OK)
@inject
async def delete_api_key(
    request: Request,
    key_id: str,
    api_key_service: ApiKeyService = Depends(Provide[AppContainer.api_key_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    """Deletes an API Key and all associated permission records (cascading delete)."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    resolved_key_id = await resolve_apikey_id(key_id, api_key_service, tenant_id)
    is_success = await api_key_service.delete(resolved_key_id, tenant_id)
    if not is_success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found")
    return {"message": f"API Key {key_id} deleted successfully"}

@router.get("/{key_id}/permissions", response_model=List[ApiKeyPermissionResponse])
@inject
async def get_key_permissions(
    request: Request,
    key_id: str,
    api_key_service: ApiKeyService = Depends(Provide[AppContainer.api_key_service]),
    permission_service: ApiKeyPermissionService = Depends(Provide[AppContainer.api_key_permission_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.COLLECTION))
):
    """Retrieves all permission records associated with a specific API Key."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    resolved_key_id = await resolve_apikey_id(key_id, api_key_service, tenant_id)
    qa = QueryArgs(where=[Filter(field="apikey_id", op=FilterOp.EQUAL, value=resolved_key_id)])
    perms = await permission_service.find(qa, tenant_id)
    return perms

@router.post("/{key_id}/permissions", response_model=ApiKeyPermissionResponse, status_code=status.HTTP_201_CREATED)
@inject
async def add_permission_to_key(
    request: Request,
    key_id: str,
    permission_data: ApiKeyPermissionCreate,
    api_key_service: ApiKeyService = Depends(Provide[AppContainer.api_key_service]),
    permission_service: ApiKeyPermissionService = Depends(Provide[AppContainer.api_key_permission_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    """Adds a new privilege (permission) to an existing API Key."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    resolved_key_id = await resolve_apikey_id(key_id, api_key_service, tenant_id)
    
    # Check if duplicate permission already exists
    qa = QueryArgs(
        where=[
            Filter(field="apikey_id", op=FilterOp.EQUAL, value=resolved_key_id),
            Filter(field="target_collection_id", op=FilterOp.EQUAL, value=permission_data.target_collection_id),
            Filter(field="target_map_id", op=FilterOp.EQUAL, value=permission_data.target_map_id),
            Filter(field="target_layer_id", op=FilterOp.EQUAL, value=permission_data.target_layer_id),
            Filter(field="access_level", op=FilterOp.EQUAL, value=permission_data.access_level.value)
        ]
    )
    existing = await permission_service.find_one(qa, tenant_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Record already exists"
        )
        
    new_perm = ApiKeyPermissionCreate(
        target_collection_id=permission_data.target_collection_id,
        target_map_id=permission_data.target_map_id,
        target_layer_id=permission_data.target_layer_id,
        access_level=permission_data.access_level
    )
    # Exclude unset fields when creating DB record
    dict_payload = new_perm.model_dump()
    dict_payload["apikey_id"] = resolved_key_id
    
    # Create manually in repository
    async with permission_service.repo._db.session() as session:
        db_perm = ApiKeyPermissionEntity(**dict_payload)
        db_perm.tenant_id = tenant_id
        session.add(db_perm)
        await session.commit()
        await session.refresh(db_perm)
        
    return ApiKeyPermissionResponse.model_validate(permission_service.repo.dict(db_perm))

@router.delete("/permissions/{permission_id}", status_code=status.HTTP_200_OK)
@inject
async def remove_permission_from_key(
    request: Request,
    permission_id: uuid.UUID,
    permission_service: ApiKeyPermissionService = Depends(Provide[AppContainer.api_key_permission_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    """Removes a specific privilege (permission) record from the system."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    is_success = await permission_service.delete(permission_id, tenant_id)
    if not is_success:
        raise HTTPException(status_code=404, detail="Permission record not found")
    return {"message": f"Permission {permission_id} successfully removed"}

@router.post("/exchange_token", response_model=TokenResponse)
async def exchange_api_key_for_token(
    verified_key: ApiKeyEntity = Depends(get_verified_api_key)
):
    """Exchanges a secure, long-lived API Key for a short-lived bearer JWT."""
    encoded_jwt, expiration_time = create_jwt(
        verified_key.id,
        verified_key.public_lookup_id,
        TOKEN_EXPIRATION_MINUTES,
        tenant_id=verified_key.tenant_id
    )
    return TokenResponse(
        access_token=encoded_jwt,
        expires_at=expiration_time,
        user_id=verified_key.id,
        public_lookup_id=verified_key.public_lookup_id
    )
