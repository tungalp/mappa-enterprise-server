from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
import uuid

from dependency_injector.wiring import Provide, inject
from desktop_mobile.config.app_container import AppContainer
from desktop_mobile.services.business_services import CollectionService
from desktop_mobile.services.auth import check_permission, ResourceAccess, ResourceType
from desktop_mobile.models.schemas import CollectionResponse, CollectionCreate
from mapa.core.data.query_args import QueryArgs

router = APIRouter()

@router.get("/{collection_id}", response_model=CollectionResponse)
@inject
async def get_collection(
    request: Request,
    collection_id: uuid.UUID,
    collection_service: CollectionService = Depends(Provide[AppContainer.collection_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.COLLECTION))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    col = await collection_service.get(collection_id, tenant_id)
    if not col:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return col

@router.get("/", response_model=List[CollectionResponse])
@inject
async def get_all_collections(
    request: Request,
    collection_service: CollectionService = Depends(Provide[AppContainer.collection_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.COLLECTION))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    qa = QueryArgs(limit=100)
    cols = await collection_service.find(qa, tenant_id)
    return cols

@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_collection(
    request: Request,
    collection_data: CollectionCreate,
    collection_service: CollectionService = Depends(Provide[AppContainer.collection_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    user_id = request.user.public_lookup_id if hasattr(request.user, "public_lookup_id") else "system"
    col = await collection_service.create(collection_data, tenant_id, user_id)
    return col

@router.put("/{collection_id}", response_model=CollectionResponse)
@inject
async def update_collection(
    request: Request,
    collection_id: uuid.UUID,
    collection_data: CollectionCreate,
    collection_service: CollectionService = Depends(Provide[AppContainer.collection_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    user_id = request.user.public_lookup_id if hasattr(request.user, "public_lookup_id") else "system"
    col = await collection_service.update(collection_id, collection_data, tenant_id, user_id)
    if not col:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return col

@router.delete("/{collection_id}", status_code=status.HTTP_200_OK)
@inject
async def delete_collection(
    request: Request,
    collection_id: uuid.UUID,
    collection_service: CollectionService = Depends(Provide[AppContainer.collection_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    is_success = await collection_service.delete(collection_id, tenant_id)
    if not is_success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return {"message": f"Collection {collection_id} deleted successfully"}

@router.post("/{collection_id}/maps/{map_id}", status_code=status.HTTP_201_CREATED)
@inject
async def add_map_to_collection(
    request: Request,
    collection_id: uuid.UUID,
    map_id: uuid.UUID,
    collection_service: CollectionService = Depends(Provide[AppContainer.collection_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    is_success = await collection_service.add_map_relation(collection_id, map_id, tenant_id)
    if not is_success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to link Map to Collection")
    return {"message": f"Linked Map {map_id} to Collection {collection_id}"}

@router.delete("/{collection_id}/maps/{map_id}", status_code=status.HTTP_200_OK)
@inject
async def remove_map_from_collection(
    request: Request,
    collection_id: uuid.UUID,
    map_id: uuid.UUID,
    collection_service: CollectionService = Depends(Provide[AppContainer.collection_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    is_success = await collection_service.remove_map_relation(collection_id, map_id, tenant_id)
    if not is_success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link does not exist")
    return {"message": f"Unlinked Map {map_id} from Collection {collection_id}"}
