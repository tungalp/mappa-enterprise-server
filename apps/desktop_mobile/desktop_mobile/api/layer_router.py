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
from desktop_mobile.shared.utils import rewrite_presigned_url
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
        url_path = f"file_stores/{layer_id}/{file_name}"
    try:
        upload_url = layer_service.minio_service.get_presigned_upload_url(url_path, bucket=bucket)
        upload_url = rewrite_presigned_url(request, upload_url)
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
    as_geojson: bool = False,
    layer_service: LayerService = Depends(Provide[AppContainer.layer_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.LAYER))
):
    """Generates a direct pre-signed URL from S3/MinIO for the physical layer files, or converts vector files to GeoJSON."""
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

    # If requested as GeoJSON for GPKG, Shapefile, KML, GDB, etc.
    if as_geojson:
        try:
            # Parse real S3 path and sub-layer name (if pipe-separated)
            url_parts = db_layer.url_path.split("|")
            real_s3_path = url_parts[0]
            layer_name = None
            for part in url_parts[1:]:
                if part.startswith("layername="):
                    layer_name = part.split("=", 1)[1]

            # Dynamic resolution of parent S3 dataset path if the path is relative (starts with '|')
            if not real_s3_path or real_s3_path.startswith("|"):
                from sqlalchemy import text
                async with layer_service.repo._db.session() as session:
                    stmt = text("""
                        SELECT ml.map_id 
                        FROM desktop_mobile.map_layer ml
                        WHERE ml.layer_id = :layer_id
                        LIMIT 1;
                    """)
                    res = await session.execute(stmt, {"layer_id": layer_id})
                    row = res.fetchone()
                    if row:
                        map_id = row[0]
                        prefix = f"maps/{map_id}/"
                        objects = layer_service.minio_service.list_objects(prefix=prefix, bucket=db_layer.bucket)
                        for obj in objects:
                            if obj.object_name.lower().endswith(".gdb.zip"):
                                real_s3_path = obj.object_name
                                break

            file_bytes = layer_service.minio_service.get_object(real_s3_path, bucket=db_layer.bucket)
            if not file_bytes:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file empty or missing in storage")

            if t_lower == ".geojson" and not layer_name:
                import json
                from fastapi.responses import JSONResponse
                geojson_data = json.loads(file_bytes.decode("utf-8"))
                return JSONResponse(content=geojson_data)

            # Convert via Geopandas
            import geopandas as gpd
            import tempfile
            import os
            import json
            import zipfile
            import io
            from fastapi.responses import JSONResponse
            import fiona
            import fiona.drvsupport
            import shutil

            # Whitelist custom Fiona drivers (KML, KMZ, Personal Geodatabase)
            fiona.drvsupport.supported_drivers['KML'] = 'r'
            fiona.drvsupport.supported_drivers['LIBKML'] = 'r'
            fiona.drvsupport.supported_drivers['KMZ'] = 'r'
            fiona.drvsupport.supported_drivers['PGeo'] = 'r'
            fiona.drvsupport.supported_drivers['MDB'] = 'r'

            temp_dir = tempfile.mkdtemp()
            try:
                # Check if archive is zipped
                is_zip = real_s3_path.lower().endswith(".zip") or real_s3_path.lower().endswith(".kmz") or real_s3_path.lower().endswith(".gdb.zip")
                target_read_path = None

                if is_zip:
                    # Unzip to temp directory
                    with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as z:
                        z.extractall(temp_dir)
                    
                    # Look for spatial format indicators
                    for root, dirs, files in os.walk(temp_dir):
                        # 1. Look for .gdb directory
                        for d in dirs:
                            if d.lower().endswith(".gdb"):
                                target_read_path = os.path.join(root, d)
                                break
                        if target_read_path:
                            break
                        
                        # 2. Look for .shp file
                        for f in files:
                            if f.lower().endswith(".shp"):
                                target_read_path = os.path.join(root, f)
                                break
                        if target_read_path:
                            break

                        # 3. Look for .kml file
                        for f in files:
                            if f.lower().endswith(".kml"):
                                target_read_path = os.path.join(root, f)
                                break
                        if target_read_path:
                            break
                else:
                    # Single unzipped file
                    filename = real_s3_path.split("/")[-1]
                    temp_file_path = os.path.join(temp_dir, filename)
                    with open(temp_file_path, "wb") as f:
                        f.write(file_bytes)
                    target_read_path = temp_file_path

                if not target_read_path or not os.path.exists(target_read_path):
                    raise ValueError("Could not find any readable spatial dataset inside the S3 object")

                # Load dataset
                if layer_name:
                    gdf = gpd.read_file(target_read_path, layer=layer_name)
                else:
                    gdf = gpd.read_file(target_read_path)
                
                # Convert geometry to EPSG:4326 if not already
                if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
                    gdf = gdf.to_crs(epsg=4326)

                # Convert any datetime/timestamp columns to string to prevent JSON serialization errors
                import pandas as pd
                for col in gdf.columns:
                    if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                        gdf[col] = gdf[col].apply(lambda val: val.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(val) else None)

                geojson_str = gdf.to_json()
                geojson_data = json.loads(geojson_str)
                return JSONResponse(content=geojson_data)
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to convert spatial file to GeoJSON: {str(err)}"
            )

    # If it is not a synced vector format (GPKG or GeoJSON), redirect to S3 pre-signed GET URL (RAM-safe)
    if t_lower not in (".gpkg", ".geojson"):
        try:
            presigned_url = layer_service.minio_service.get_presigned_download_url(db_layer.url_path, bucket=db_layer.bucket)
            presigned_url = rewrite_presigned_url(request, presigned_url)
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

@router.get("/maps/{map_id}/data-sources")
@inject
async def download_map_data_sources(
    request: Request,
    map_id: uuid.UUID,
    layer_service: LayerService = Depends(Provide[AppContainer.layer_service]),
    _ = Depends(check_permission(action=ResourceAccess.USER, resource=ResourceType.MAP))
):
    """
    Groups all file-based vector layers in the map, downloads their parent files from S3/MinIO once,
    extracts all requested sub-layers, and returns them as a single combined GeoJSON object.
    """
    import geopandas as gpd
    import tempfile
    import os
    import json
    import zipfile
    import io
    import fiona
    import fiona.drvsupport
    import shutil
    import pandas as pd
    from fastapi.responses import JSONResponse
    from sqlalchemy import text

    # 1. Fetch all layers linked to this map
    async with layer_service.repo._db.session() as session:
        stmt = text("""
            SELECT l.id, l.name, l.type, l.url_path, l.bucket
            FROM desktop_mobile.layer l
            JOIN desktop_mobile.map_layer ml ON l.id = ml.layer_id
            WHERE ml.map_id = :map_id;
        """)
        res = await session.execute(stmt, {"map_id": map_id})
        rows = res.fetchall()

    # 2. Filter file-based vector layers (exclude raster and online services)
    vector_extensions = (".geojson", ".gpkg", ".shp", ".gdb", ".zip", ".kml", ".kmz", ".mdb")
    file_layers = []
    for lyr_id, name, ltype, url_path, bucket in rows:
        if not ltype or not url_path:
            continue
        t_lower = ltype.lower()
        # Exclude raster types
        if any(x in t_lower for x in ("tif", "ecw", "pdf", "png", "jpg", "jpeg", "gif")):
            continue
        # Check if it is a vector file based layer
        is_vector_file = any(t_lower == ext or t_lower.endswith(ext) or ext.endswith(t_lower) for ext in vector_extensions)
        if is_vector_file:
            file_layers.append({
                "id": lyr_id,
                "name": name,
                "type": ltype,
                "url_path": url_path,
                "bucket": bucket or "desktop-mobile"
            })

    if not file_layers:
        return JSONResponse(content={})

    # 3. List objects under maps/{map_id}/ once to resolve any relative paths
    default_gdb_path = None
    try:
        objects = layer_service.minio_service.list_objects(prefix=f"maps/{map_id}/")
        for obj in objects:
            if obj.object_name.lower().endswith(".gdb.zip"):
                default_gdb_path = obj.object_name
                break
    except Exception as e:
        print(f"[Batch Download] Failed to list S3 objects for map {map_id}: {e}")

    # 4. Group layers by parent S3 path
    grouped_layers = {}
    for lyr in file_layers:
        url_parts = lyr["url_path"].split("|")
        parent_path = url_parts[0]
        layer_name = None
        for part in url_parts[1:]:
            if part.startswith("layername="):
                layer_name = part.split("=", 1)[1]

        if not parent_path or parent_path.startswith("|"):
            parent_path = default_gdb_path

        if not parent_path:
            continue

        key = (parent_path, lyr["bucket"])
        if key not in grouped_layers:
            grouped_layers[key] = []
        grouped_layers[key].append({
            "id": lyr["id"],
            "name": lyr["name"],
            "type": lyr["type"],
            "layer_name": layer_name
        })

    # 5. Whitelist custom fiona drivers
    fiona.drvsupport.supported_drivers['KML'] = 'r'
    fiona.drvsupport.supported_drivers['LIBKML'] = 'r'
    fiona.drvsupport.supported_drivers['KMZ'] = 'r'
    fiona.drvsupport.supported_drivers['PGeo'] = 'r'
    fiona.drvsupport.supported_drivers['MDB'] = 'r'

    result = {}

    # 6. Process each parent file group
    for (parent_path, bucket), layers_in_group in grouped_layers.items():
        try:
            # Download parent file once
            file_bytes = layer_service.minio_service.get_object(parent_path, bucket=bucket)
            if not file_bytes:
                continue

            temp_dir = tempfile.mkdtemp()
            try:
                is_zip = parent_path.lower().endswith(".zip") or parent_path.lower().endswith(".kmz") or parent_path.lower().endswith(".gdb.zip")
                target_read_path = None

                if is_zip:
                    with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as z:
                        z.extractall(temp_dir)
                    
                    for root, dirs, files in os.walk(temp_dir):
                        for d in dirs:
                            if d.lower().endswith(".gdb"):
                                target_read_path = os.path.join(root, d)
                                break
                        if target_read_path:
                            break
                        for f in files:
                            if f.lower().endswith(".shp") or f.lower().endswith(".kml"):
                                target_read_path = os.path.join(root, f)
                                break
                        if target_read_path:
                            break
                else:
                    filename = parent_path.split("/")[-1]
                    temp_file_path = os.path.join(temp_dir, filename)
                    with open(temp_file_path, "wb") as f:
                        f.write(file_bytes)
                    target_read_path = temp_file_path

                if not target_read_path or not os.path.exists(target_read_path):
                    continue

                # Read each layer from the target extracted path
                for lyr in layers_in_group:
                    try:
                        l_name = lyr["layer_name"]
                        if l_name:
                            gdf = gpd.read_file(target_read_path, layer=l_name)
                        else:
                            gdf = gpd.read_file(target_read_path)

                        if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
                            gdf = gdf.to_crs(epsg=4326)

                        # Clean Timestamp columns
                        for col in gdf.columns:
                            if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                                gdf[col] = gdf[col].apply(lambda val: val.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(val) else None)

                        geojson_str = gdf.to_json()
                        result[str(lyr["id"])] = json.loads(geojson_str)
                    except Exception as lyr_err:
                        print(f"[Batch Download] Failed to read sub-layer {lyr['name']} ({lyr['id']}): {lyr_err}")

            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as group_err:
            print(f"[Batch Download] Failed to process parent file {parent_path}: {group_err}")

    return JSONResponse(content=result)

