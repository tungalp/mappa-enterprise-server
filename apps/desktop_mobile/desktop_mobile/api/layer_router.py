from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, UploadFile, File
from pydantic import ValidationError
from typing import List, Optional
import uuid
import json

from dependency_injector.wiring import Provide, inject
from desktop_mobile.config.app_container import AppContainer
from desktop_mobile.services.business_services import LayerService
from desktop_mobile.services.auth import check_permission, ResourceAccess, ResourceType
from desktop_mobile.models.schemas import LayerResponse, LayerCreate, PresignedUrlResponse
from mapa.core.data.query_args import QueryArgs

router = APIRouter()

async def get_layer_create_data_from_form(
    layer_data: str = Form(..., description="JSON string of layer data")
) -> LayerCreate:
    """Dependency to parse and validate layer data from form"""
    try:
        layer_data_dict = json.loads(layer_data)
        return LayerCreate(**layer_data_dict)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Invalid JSON in layer_data")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

@router.get("/presigned-upload-url", response_model=PresignedUrlResponse)
@inject
async def get_presigned_upload_url(
    request: Request,
    file_name: str,
    bucket: Optional[str] = None,
    map_id: Optional[uuid.UUID] = None,
    layer_service: LayerService = Depends(Provide[AppContainer.layer_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.LAYER))
):
    """Generates a direct pre-signed PUT S3/MinIO upload URL for large files."""
    if map_id:
        url_path = f"maps/{map_id}/{file_name}"
    else:
        layer_id = uuid.uuid4()
        url_path = f"layers/{layer_id}/{file_name}"
    try:
        upload_url = layer_service.minio_service.get_presigned_upload_url(url_path, bucket=bucket)
        return PresignedUrlResponse(upload_url=upload_url, url_path=url_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate pre-signed upload URL: {str(e)}"
        )

@router.get("/{layer_id}", response_model=LayerResponse)
@inject
async def get_layer(
    request: Request,
    layer_id: uuid.UUID,
    layer_service: LayerService = Depends(Provide[AppContainer.layer_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.LAYER))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    layer = await layer_service.get(layer_id, tenant_id)
    if not layer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer not found")
    return layer

@router.get("/", response_model=List[LayerResponse])
@inject
async def get_all_layers(
    request: Request,
    layer_service: LayerService = Depends(Provide[AppContainer.layer_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.LAYER))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    qa = QueryArgs(limit=100)
    layers = await layer_service.find(qa, tenant_id)
    return layers

@router.post("/{map_id}", response_model=LayerResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_layer(
    request: Request,
    map_id: uuid.UUID,
    layer_data: LayerCreate = Depends(get_layer_create_data_from_form),
    file_store: Optional[UploadFile] = File(None),
    layer_service: LayerService = Depends(Provide[AppContainer.layer_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.MAP))
):
    """Create a layer linked to a map, with optional S3 file upload."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    user_id = request.user.public_lookup_id if hasattr(request.user, "public_lookup_id") else "system"
    
    file_data = None
    file_name = None
    if file_store and file_store.filename:
        file_data = await file_store.read()
        file_name = file_store.filename

    try:
        layer = await layer_service.create_layer(
            map_id=map_id,
            layer_data=layer_data,
            file_name=file_name,
            file_data=file_data,
            tenant_id=tenant_id,
            user_id=user_id
        )
        return layer
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{layer_id}", response_model=LayerResponse)
@inject
async def update_layer(
    request: Request,
    layer_id: uuid.UUID,
    layer_data: LayerCreate = Depends(get_layer_create_data_from_form),
    file_store: Optional[UploadFile] = File(None),
    layer_service: LayerService = Depends(Provide[AppContainer.layer_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.LAYER))
):
    """Updates a layer's styling, properties, or uploads delta-sync changes for GeoJSON/GPKG."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    user_id = request.user.public_lookup_id if hasattr(request.user, "public_lookup_id") else "system"
    
    file_data = None
    file_name = None
    if file_store and file_store.filename:
        file_data = await file_store.read()
        file_name = file_store.filename

    try:
        layer = await layer_service.update_layer(
            layer_id=layer_id,
            layer_data=layer_data,
            file_name=file_name,
            file_data=file_data,
            tenant_id=tenant_id,
            user_id=user_id
        )
        return layer
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{layer_id}", status_code=status.HTTP_200_OK)
@inject
async def delete_layer(
    request: Request,
    layer_id: uuid.UUID,
    layer_service: LayerService = Depends(Provide[AppContainer.layer_service]),
    _ = Depends(check_permission(action=ResourceAccess.ADMIN, resource=ResourceType.LAYER))
):
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    try:
        await layer_service.delete_layer(layer_id, tenant_id)
        return {"message": f"Layer {layer_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{layer_id}/data-source")
@inject
async def download_layer_file(
    request: Request,
    layer_id: uuid.UUID,
    layer_service: LayerService = Depends(Provide[AppContainer.layer_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.LAYER))
):
    """Generates a direct pre-signed URL from S3/MinIO for the physical layer files."""
    tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else None
    db_layer = await layer_service.get(layer_id, tenant_id)
    if not db_layer or not db_layer.url_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer or physical file not found")
    
    # Check if the layer is file-based
    from desktop_mobile.models.entities import LayerFileType
    t_lower = db_layer.type.lower()
    is_file_based = any(t_lower == ext or t_lower.endswith(ext) or ext.endswith(t_lower) for ext in LayerFileType)
    
    if not is_file_based:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Layer is service-based (WMS/WFS); no S3 download available")

    # If it is not a synced vector format (GPKG or GeoJSON), redirect to S3 pre-signed GET URL (RAM-safe)
    if t_lower not in (".gpkg", ".geojson"):
        try:
            presigned_url = layer_service.minio_service.get_presigned_download_url(db_layer.url_path, bucket=db_layer.bucket)
            from fastapi.responses import RedirectResponse
            return RedirectResponse(presigned_url, status_code=307)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File redirection failed: {str(e)}")
    
    # Synced vector format (GPKG and GeoJSON): stream directly from FastAPI
    from fastapi.responses import StreamingResponse
    import io

    try:
        file_bytes = layer_service.minio_service.get_object(db_layer.url_path, bucket=db_layer.bucket)
        filename = db_layer.url_path.split("/")[-1]
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File download failed: {str(e)}")
