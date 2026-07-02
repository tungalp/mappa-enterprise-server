from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, UploadFile, File, Query
from pydantic import ValidationError
from typing import List, Optional
import uuid
import json

from dependency_injector.wiring import Provide, inject
from desktop_mobile.config.app_container import AppContainer
from desktop_mobile.services.business_services import MapService
from desktop_mobile.services.auth import check_permission, ResourceAccess, ResourceType
from desktop_mobile.models.schemas import MapResponse, MapCreate, MergedMapResponse
from desktop_mobile.shared.utils import rewrite_presigned_url
from mapa.core.data.query_args import QueryArgs

router = APIRouter()

async def get_map_create_data_from_form(
    map_data: str = Form(..., description="JSON string of map data")
) -> MapCreate:
    """Dependency to parse and validate map data from form"""
    try:
        map_data_dict = json.loads(map_data)
        return MapCreate(**map_data_dict)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Invalid JSON in map_data")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

@router.get("/{map_id}", response_model=MergedMapResponse)
@inject
async def get_map(
    request: Request,
    map_id: uuid.UUID,
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.MAP))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    try:
        map_obj = await map_service.get_map_merged(map_id, tenant_id)
        return map_obj
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/", response_model=List[MergedMapResponse])
@inject
async def get_all_maps(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    name: Optional[str] = Query(None),
    collection_id: Optional[uuid.UUID] = Query(None),
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.MAP))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    maps = await map_service.get_maps_merged(
        skip=skip,
        limit=limit,
        name=name,
        collection_id=collection_id,
        tenant_id=tenant_id
    )
    return maps

@router.post("/{collection_id}", response_model=MapResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_map(
    request: Request,
    collection_id: uuid.UUID,
    map_data: MapCreate = Depends(get_map_create_data_from_form),
    project_file: Optional[UploadFile] = File(None),
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.COLLECTION))
):
    """Create map within a collection with form data including QGIS project file upload"""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    user_id = request.user.public_lookup_id if hasattr(request.user, "public_lookup_id") else "system"
    
    file_data = None
    file_name = None
    if project_file and project_file.filename:
        file_data = await project_file.read()
        file_name = project_file.filename

    try:
        map_obj = await map_service.create_map(
            collection_id=collection_id,
            map_data=map_data,
            file_name=file_name,
            file_data=file_data,
            tenant_id=tenant_id,
            user_id=user_id
        )
        return map_obj
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{map_id}", response_model=MapResponse)
@inject
async def update_map(
    request: Request,
    map_id: uuid.UUID,
    map_data: MapCreate = Depends(get_map_create_data_from_form),
    project_file: Optional[UploadFile] = File(None),
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.MAP))
):
    """Updates map metadata or uploads a new QGIS .qgz project configuration file."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    user_id = request.user.public_lookup_id if hasattr(request.user, "public_lookup_id") else "system"

    # Fetch existing Map record
    db_map = await map_service.get(map_id, tenant_id)
    if not db_map:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

    # Update general properties
    update_model = MapCreate(
        name=map_data.name,
        description=map_data.description,
        web_map_id=map_data.web_map_id
    )
    
    # Run the entity update
    await map_service.update(map_id, update_model, tenant_id, user_id)

    # Process and upload project file if provided
    if project_file and project_file.filename:
        file_data = await project_file.read()
        await map_service.upload_project_file(
            map_id=map_id,
            file_name=project_file.filename,
            file_data=file_data,
            tenant_id=tenant_id,
            user_id=user_id
        )

    return await map_service.get(map_id, tenant_id)

@router.delete("/{map_id}", status_code=status.HTTP_200_OK)
@inject
async def delete_map(
    request: Request,
    map_id: uuid.UUID,
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.MAP))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    try:
        await map_service.delete_map(map_id, tenant_id)
        return {"message": f"Map {map_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- QGIS .qgz Project Configuration Upload/Download via MinIO ---
@router.post("/{map_id}/project_file", response_model=MapResponse)
@inject
async def upload_map_project_file(
    request: Request,
    map_id: uuid.UUID,
    file: UploadFile = File(...),
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.MAP))
):
    """Uploads QGIS .qgz project configurations directly to MinIO, updating the map's metadata url."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    user_id = request.user.public_lookup_id if hasattr(request.user, "public_lookup_id") else "system"
    
    file_data = await file.read()
    updated_map = await map_service.upload_project_file(
        map_id=map_id,
        file_name=file.filename or "project.qgz",
        file_data=file_data,
        tenant_id=tenant_id,
        user_id=user_id
    )
    return updated_map

@router.get("/{map_id}/project_file")
@inject
async def download_map_project_file(
    request: Request,
    map_id: uuid.UUID,
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.MAP))
):
    """Generates a highly-performant, direct presigned download URL from MinIO for QGIS .qgz files."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    db_map = await map_service.get(map_id, tenant_id)
    
    if not db_map or not db_map.project_file_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Map project file not found or not uploaded yet"
        )
        
    presigned_url = map_service.minio_service.get_presigned_download_url(db_map.project_file_url)
    presigned_url = rewrite_presigned_url(request, presigned_url)
    return {"url": presigned_url}

# --- Map-Layer Link Management ---
@router.post("/{map_id}/layers/{layer_id}", status_code=status.HTTP_201_CREATED)
@inject
async def add_layer_to_map(
    request: Request,
    map_id: uuid.UUID,
    layer_id: uuid.UUID,
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.MAP))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    is_success = await map_service.add_layer_relation(map_id, layer_id, tenant_id)
    if not is_success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to link Layer to Map")
    return {"message": f"Linked Layer {layer_id} to Map {map_id}"}

@router.delete("/{map_id}/layers/{layer_id}", status_code=status.HTTP_200_OK)
@inject
async def remove_layer_from_map(
    request: Request,
    map_id: uuid.UUID,
    layer_id: uuid.UUID,
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.MAP))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    is_success = await map_service.remove_layer_relation(map_id, layer_id, tenant_id)
    if not is_success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link does not exist")
    return {"message": f"Unlinked Layer {layer_id} from Map {map_id}"}

@router.post("/fonts/upload", status_code=status.HTTP_201_CREATED)
@inject
async def upload_custom_font(
    request: Request,
    file: UploadFile = File(...),
    map_service: MapService = Depends(Provide[AppContainer.map_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.MAP))
):
    """Uploads a custom TTF/OTF font file, saves it to MinIO/S3, and synchronizes it locally for styling."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    file_data = await file.read()
    try:
        object_name = map_service.upload_custom_font(file.filename, file_data)
        return {
            "message": f"Font {file.filename} uploaded and synchronized successfully",
            "s3_path": object_name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
