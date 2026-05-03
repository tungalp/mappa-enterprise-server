import json
from typing import Any, Dict, List


from dependency_injector.wiring import Provide, inject
from mapa.app.params import fields_param, query_param
from mapa.core.data.query_args import QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.security import authorize
from mapa.spatial.file_store.file_store_model import CreateFileStore, UpdateFileStore
from mapa.spatial.file_store.file_store_service import FileStoreService, GeoJSONConflictResolver
from mapa.spatial.constant import ApiScopeType
from fastapi import (APIRouter, Body, Depends, HTTPException, Query, Request,
                     status)
from fastapi.responses import JSONResponse
from spatial.config.app_container import AppContainer
from spatial.file_store.minio_service import MinioService
import uuid


from mapa.spatial.constant import FileType

router = APIRouter()


@router.get("/{file_store_id}", response_model=Any)
@authorize()
@inject
async def find(
    request: Request,
    file_store_id: str,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service]),
    minio_service: MinioService = Depends(Provide[AppContainer.minio_service])
):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    file_store = await file_store_service.get(file_store_id, tenant_id, field_list)
    
    if not file_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    # If file_url is present, generate a pre-signed download URL
    if file_store.file_url:
        file_store.file_url = minio_service.get_presigned_download_url(file_store.file_url)

    # Reconstruct geojson now and renew download time and send to user
    if file_store.file_format == FileType.geojson:
        resolver = GeoJSONConflictResolver()
        # For now, we'll skip the processing if it's already on MinIO and just return the URL
        # The frontend will download and process if needed.
        pass


    return file_store


@router.get("/", response_model=PagingResult[Any])
@authorize()
@inject
async def find_all(
    request: Request,
    query_args: QueryArgs = query_param(),
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service]),
    minio_service: MinioService = Depends(Provide[AppContainer.minio_service])
):
    """Api bilgilerini getirir"""

    tenant_id = request.user.tenant_id
    result = await file_store_service.get_all(tenant_id, query_args)
    
    # Generate pre-signed URLs for all items in the list
    for item in result.items:
        if item.file_url:
            item.file_url = minio_service.get_presigned_download_url(item.file_url)

    return result


@router.post("/", status_code=201, response_model=ActionResult)
@authorize()
@inject
async def create(
    request: Request,
    items: List[CreateFileStore] = Body(),
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service]),
    minio_service: MinioService = Depends(Provide[AppContainer.minio_service])
):
    tenant_id = request.user.tenant_id
    user_id = request.user.sub
    
    # Convert base64 data to geojson and row_guid before saving Bekir 10.09.2025
    for item in items:
        if item.file_format == FileType.geojson:
            resolver = GeoJSONConflictResolver()
            
            # URL or Data provided
            if item.data:
                file_geojson = item.data
                # If no file_url provided, we need to generate one
                if not item.file_url:
                    item.file_url = f"{uuid.uuid4()}-imported.geojson"
            elif item.file_url:
                # Download from MinIO
                raw_data = minio_service.get_object(item.file_url)
                file_geojson = json.loads(raw_data.decode('utf-8'))
            
            if file_geojson:
                file_geojson = resolver.add_guid_to_geojson(file_geojson)
                file_geojson = resolver.add_update_download_time(file_geojson)
                
                # Re-upload to MinIO
                processed_data = json.dumps(file_geojson, separators=(',', ':')).encode('utf-8')
                minio_service.put_object(item.file_url, processed_data, content_type="application/json")

    file_stores = await file_store_service.create_all(items, tenant_id, user_id)

    # Generate pre-signed URLs for the response
    for fs in file_stores:
        if fs.file_url:
            fs.file_url = minio_service.get_presigned_download_url(fs.file_url)

    result = ActionResult(success=True, items=file_stores)

    return result


@router.put("/{file_store_id}", status_code=201, response_model=ActionResult)
@authorize()
@inject
async def update(
    request: Request,
    file_store_id: str,
    item: UpdateFileStore = Body(),
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service]),
    minio_service: MinioService = Depends(Provide[AppContainer.minio_service])
):
    tenant_id = request.user.tenant_id
    user_id = request.user.sub
    
    # Convert base64 data to geojson and row_guid before saving Bekir 10.09.2025
    file_geojson = None
    db_geojson = None
    resolver = GeoJSONConflictResolver()
    
    # Fetch original first to get old file_url
    db_file_store = await file_store_service.get(file_store_id, tenant_id)
    old_object_name = db_file_store.file_url

    if item.file_format == FileType.geojson:
        # URL or Data provided
        if item.data:
            file_geojson = item.data
        elif item.file_url:
            raw_data = minio_service.get_object(item.file_url)
            file_geojson = json.loads(raw_data.decode('utf-8'))

        if file_geojson:
            file_geojson = resolver.add_guid_to_geojson(file_geojson)
            download_time = resolver.extract_download_time(file_geojson)

            # Fetch DB data from MinIO
            if db_file_store.file_url:
                db_raw_data = minio_service.get_object(db_file_store.file_url)
                db_geojson = json.loads(db_raw_data.decode('utf-8'))
            else:
                # This case shouldn't happen after migration, but for safety:
                raise HTTPException(status_code=400, detail="Original file data missing or not in MinIO")

            downloaded_features, red_changes = resolver.reconstruct_to_time(db_geojson, download_time)
            
            # Compare user's changes with original data
            new_features = file_geojson.get('features', [])
            comparison = resolver.merge_changes_with_conflicts(downloaded_features, new_features, red_changes)
            
            # Send comparision to db_geojson to save
            db_geojson = resolver.add_changed_features(db_geojson, comparison, user_id)
            
            # Re-upload processed data to MinIO
            processed_data = json.dumps(db_geojson, separators=(',', ':')).encode('utf-8')
            
            # Directly overwrite the existing file in MinIO to avoid storage clutter
            target_url = old_object_name
            if not target_url:
                target_url = f"{uuid.uuid4()}.geojson"
                item.file_url = target_url
            
            print(f"[FileStore] Overwriting GeoJSON in MinIO: {target_url}")
            minio_service.put_object(target_url, processed_data, content_type="application/json")

    # Write changes to DB
    # Clear 'data' before database update as it is not a real column
    # Persist the changes to the database
    # (Note: item.data is automatically excluded from the update by the model definition)
    file_stores = await file_store_service.update(file_store_id, item, tenant_id, user_id)
    
    # Reconstruct to now and send data to user back with new download_time
    if item.file_format == FileType.geojson:
        # If we updated via URL, we might want to return the updated URL or data
        # For now, let's just return the file_stores as is (which contains the URL)
        pass
        
    if not file_stores:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))

    # If file_url is present, generate a pre-signed download URL for the response
    if file_stores.file_url:
        file_stores.file_url = minio_service.get_presigned_download_url(file_stores.file_url)

    result = ActionResult(success=True, items=[file_stores], affected=1)

    return result



@router.delete("/{file_store_id}", status_code=201, response_model=ActionResult)
@authorize()
@inject
async def delete(
    request: Request,
    file_store_id: str,
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service]),
    minio_service: MinioService = Depends(Provide[AppContainer.minio_service])
):
    tenant_id = request.user.tenant_id
    
    # Fetch before delete to get file_url
    file_store = await file_store_service.get(file_store_id, tenant_id)
    if not file_store:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    
    object_name = file_store.file_url
    
    is_success = await file_store_service.delete(file_store_id, tenant_id)
    
    if is_success:
        if object_name:
            minio_service.delete_object(object_name)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
        
    result = ActionResult(success=is_success, affected=1)
    return JSONResponse(content=result.model_dump())


@router.put("/", status_code=201, response_model=ActionResult)
@authorize()
@inject
async def delete_by_ids(
    request: Request,
    file_store_ids: List[str],
    file_store_service: FileStoreService = Depends(
        Provide[AppContainer.file_store_package.file_store_service])
):
    tenant_id = request.user.tenant_id
    deleted_count = await file_store_service.delete_by_ids(file_store_ids, tenant_id)
    is_success = True if deleted_count == len(file_store_ids) else False
    if is_success == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    result = ActionResult(success=is_success, affected=deleted_count)
    return JSONResponse(content=result.model_dump())

@router.post("/upload-url")
@inject
async def get_upload_url(
    filename: str,
    minio_service: MinioService = Depends(Provide[AppContainer.minio_service])
):
    """Generates a unique object name and pre-signed PUT URL"""
    object_name = f"{uuid.uuid4()}-{filename}"
    url = minio_service.get_presigned_upload_url(object_name)
    return {"url": url, "object_name": object_name}

@router.get("/download-url/{object_name}")
@inject
async def get_download_url(
    object_name: str,
    minio_service: MinioService = Depends(Provide[AppContainer.minio_service])
):
    url = minio_service.get_presigned_download_url(object_name)
    return {"url": url}

