from typing import List, Optional, Dict, Any
import uuid
import hashlib
import json
import tempfile
import os
import shutil
import sqlite3
from datetime import datetime, timezone
from sqlalchemy import select, and_, delete, or_

from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import QueryArgs, Filter, FilterOp

from desktop_mobile.models.repositories import (
    CollectionRepository,
    MapRepository,
    LayerRepository,
    ApiKeyRepository,
    ApiKeyPermissionRepository
)
from desktop_mobile.models.entities import (
    CollectionEntity,
    MapEntity,
    LayerEntity,
    ApiKeyEntity,
    ApiKeyPermissionEntity,
    collection_map,
    map_layer,
    LayerFileType
)
from desktop_mobile.models.schemas import (
    CollectionResponse, CollectionCreate,
    MapResponse, MapCreate,
    LayerResponse, LayerCreate,
    ApiKeyResponse, ApiKeyCreate,
    ApiKeyPermissionResponse, ApiKeyPermissionCreate,
    MergedMapResponse, MergedLayerResponse
)
from desktop_mobile.services.storage import MinioService
from desktop_mobile.services.auth import generate_key_data, ResourceAccess

from desktop_mobile.shared.utils import field_changed, normalize_qml, remove_file
from desktop_mobile.shared.geojson_resolver import GeoJSONConflictResolver
from desktop_mobile.shared.gpkg_resolver import GPKGConflictResolver

class CollectionService(BaseEntityService[CollectionRepository, CollectionResponse, CollectionCreate, CollectionCreate, CollectionCreate]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, CollectionRepository, CollectionResponse)
        
    async def add_map_relation(self, collection_id: uuid.UUID, map_id: uuid.UUID, tenant_id: str | None = None) -> bool:
        """Links a Map to a Collection in the junction table."""
        async with self.repo._db.session() as session:
            c_stmt = select(CollectionEntity).where(CollectionEntity.id == collection_id)
            m_stmt = select(MapEntity).where(MapEntity.id == map_id)
            
            c_res = await session.execute(c_stmt)
            m_res = await session.execute(m_stmt)
            
            collection = c_res.scalars().first()
            map_obj = m_res.scalars().first()
            
            if not collection or not map_obj:
                return False
                
            # Check if association already exists
            check_stmt = select(collection_map).where(
                and_(
                    collection_map.c.collection_id == collection_id,
                    collection_map.c.map_id == map_id
                )
            )
            check_res = await session.execute(check_stmt)
            if check_res.first() is not None:
                return True
                
            stmt = collection_map.insert().values(
                collection_id=collection_id,
                map_id=map_id
            )
            await session.execute(stmt)
            await session.commit()
            return True

    async def remove_map_relation(self, collection_id: uuid.UUID, map_id: uuid.UUID, tenant_id: str | None = None) -> bool:
        """Unlinks a Map from a Collection in the junction table."""
        async with self.repo._db.session() as session:
            stmt = delete(collection_map).where(
                and_(
                    collection_map.c.collection_id == collection_id,
                    collection_map.c.map_id == map_id
                )
            )
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0

class MapService(BaseEntityService[MapRepository, MapResponse, MapCreate, MapCreate, MapCreate]):
    def __init__(self, async_db: AsyncDatabase, minio_service: MinioService) -> None:
        self.minio_service = minio_service
        super().__init__(async_db, MapRepository, MapResponse)
        
    async def upload_project_file(self, map_id: uuid.UUID, file_name: str, file_data: bytes, tenant_id: str | None = None, user_id: str | None = None) -> MapResponse:
        """Uploads QGIS .qgz project configurations to MinIO and updates the project_file_url."""
        object_name = f"maps/{map_id}/{uuid.uuid4()}-{file_name}"
        
        self.minio_service.put_object(object_name, file_data, content_type="application/octet-stream")
        
        async with self.repo._db.session() as session:
            stmt = select(MapEntity).where(MapEntity.id == map_id)
            if tenant_id:
                stmt = stmt.where(MapEntity.tenant_id == tenant_id)
            res = await session.execute(stmt)
            db_map = res.scalars().first()
            
            if not db_map:
                raise ValueError("Map not found")
                
            if db_map.project_file_url:
                self.minio_service.delete_object(db_map.project_file_url)
                
            db_map.project_file_url = object_name
            db_map.updater = user_id or "system"
            db_map.updated_at = datetime.now()
            await session.commit()
            
        return await self.get(map_id, tenant_id)

    async def add_layer_relation(self, map_id: uuid.UUID, layer_id: uuid.UUID, tenant_id: str | None = None) -> bool:
        """Links a Layer to a Map in the junction table."""
        async with self.repo._db.session() as session:
            m_stmt = select(MapEntity).where(MapEntity.id == map_id)
            l_stmt = select(LayerEntity).where(LayerEntity.id == layer_id)
            
            m_res = await session.execute(m_stmt)
            l_res = await session.execute(l_stmt)
            
            if not m_res.scalars().first() or not l_res.scalars().first():
                return False
                
            # Check if association already exists
            check_stmt = select(map_layer).where(
                and_(
                    map_layer.c.map_id == map_id,
                    map_layer.c.layer_id == layer_id
                )
            )
            check_res = await session.execute(check_stmt)
            if check_res.first() is not None:
                return True
                
            stmt = map_layer.insert().values(
                map_id=map_id,
                layer_id=layer_id
            )
            await session.execute(stmt)
            await session.commit()
            return True

    async def remove_layer_relation(self, map_id: uuid.UUID, layer_id: uuid.UUID, tenant_id: str | None = None) -> bool:
        """Unlinks a Layer from a Map in the junction table."""
        async with self.repo._db.session() as session:
            stmt = delete(map_layer).where(
                and_(
                    map_layer.c.map_id == map_id,
                    map_layer.c.layer_id == layer_id
                )
            )
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0

    async def check_map_name_exists_in_collection(self, session, map_name: str, collection_id: uuid.UUID) -> bool:
        """Checks if any map with the given name is already associated with the collection."""
        stmt = select(MapEntity).join(
            collection_map, MapEntity.id == collection_map.c.map_id
        ).where(
            collection_map.c.collection_id == collection_id
        )
        res = await session.execute(stmt)
        maps = res.scalars().all()
        for m in maps:
            if m.name.lower() == map_name.lower():
                return True
        return False

    async def create_map(
        self,
        collection_id: uuid.UUID,
        map_data: MapCreate,
        file_name: Optional[str] = None,
        file_data: Optional[bytes] = None,
        tenant_id: str | None = None,
        user_id: str | None = None
    ) -> MapResponse:
        creator_id = user_id or "system"
        map_id = map_data.web_map_id or uuid.uuid4()
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        async with self.repo._db.session() as session:
            # Check duplicate map name in collection
            if await self.check_map_name_exists_in_collection(session, map_data.name, collection_id):
                raise ValueError(f"Duplicate map name '{map_data.name}' in collection ID {collection_id}.")
            
            project_file_url = None
            if file_data and file_name:
                if not file_name.lower().endswith('.qgz'):
                    raise ValueError("Only QGZ files allowed")
                if len(file_data) > 50 * 1024 * 1024:
                    raise ValueError("File too large (max 50MB)")
                
                project_file_url = f"maps/{map_id}/{uuid.uuid4()}-{file_name}"
                self.minio_service.put_object(project_file_url, file_data, content_type="application/octet-stream")

            new_map = MapEntity(
                id=map_id,
                name=map_data.name,
                description=map_data.description,
                web_map_id=map_data.web_map_id,
                project_file_url=project_file_url,
                creator=creator_id,
                updater=creator_id,
                created_at=now,
                updated_at=now,
                tenant_id=tenant_id
            )
            session.add(new_map)
            await session.flush()
            
            stmt = collection_map.insert().values(
                collection_id=collection_id,
                map_id=map_id
            )
            await session.execute(stmt)
            await session.commit()
            
        return await self.get(map_id, tenant_id)

    async def delete_map(self, map_id: uuid.UUID, tenant_id: str | None = None) -> bool:
        print(f"\n[delete_map] === START MAP DELETION: {map_id} ===")
        async with self.repo._db.session() as session:
            # 1. Fetch map first to verify it exists and get project file URL
            stmt = select(MapEntity).where(MapEntity.id == map_id)
            if tenant_id:
                stmt = stmt.where(MapEntity.tenant_id == tenant_id)
            res = await session.execute(stmt)
            db_map = res.scalars().first()
            if not db_map:
                print(f"[delete_map] ERROR: Map {map_id} not found in database!")
                raise ValueError("Map not found")

            # Get all layer IDs linked to this map
            l_stmt = select(map_layer.c.layer_id).where(map_layer.c.map_id == map_id)
            l_res = await session.execute(l_stmt)
            layer_ids = [row[0] for row in l_res.fetchall()]
            print(f"[delete_map] Map {map_id} is associated with layer IDs: {layer_ids}")

            layers_to_delete = []
            for layer_id in layer_ids:
                # Count other maps linked to this layer
                count_stmt = select(map_layer.c.map_id).where(
                    and_(
                        map_layer.c.layer_id == layer_id,
                        map_layer.c.map_id != map_id
                    )
                )
                count_res = await session.execute(count_stmt)
                other_maps = count_res.fetchall()
                print(f"[delete_map] Layer {layer_id} is linked to other maps: {[m[0] for m in other_maps]}")
                if not other_maps:
                    layers_to_delete.append(layer_id)

            print(f"[delete_map] Exclusive layers determined to be deleted: {layers_to_delete}")

            exclusive_layers = []
            if layers_to_delete:
                # Fetch all exclusive LayerEntities before we clear the junction table
                layer_stmt = select(LayerEntity).where(LayerEntity.id.in_(layers_to_delete))
                layer_res = await session.execute(layer_stmt)
                exclusive_layers = layer_res.scalars().all()

            # 2. Deletes the collection-map relations
            print(f"[delete_map] Clearing collection_map relations for map {map_id}...")
            col_rel_stmt = delete(collection_map).where(collection_map.c.map_id == map_id)
            await session.execute(col_rel_stmt)

            # 3. Clean up all associations in the map_layer junction table for this map first
            print(f"[delete_map] Clearing map_layer junction table rows for map {map_id}...")
            map_layer_rel_stmt = delete(map_layer).where(map_layer.c.map_id == map_id)
            await session.execute(map_layer_rel_stmt)

            # 4. Physically delete the QGIS project file from MinIO if it exists
            if db_map.project_file_url:
                print(f"[delete_map] Physically deleting QGIS project file from MinIO: {db_map.project_file_url}...")
                self.minio_service.delete_object(db_map.project_file_url)

            # 5. Delete exclusive layers and their physical S3 files
            if exclusive_layers:
                for db_layer in exclusive_layers:
                    print(f"\n[delete_map] Processing exclusive layer ID: {db_layer.id}, Name: '{db_layer.name}', url_path: '{db_layer.url_path}'")
                    if db_layer.url_path:
                        # Extract the clean file path from QGIS provider options (split by '|' if present)
                        clean_url_path = db_layer.url_path.split('|')[0]
                        prefix = None
                        if '/' in clean_url_path:
                            # The folder prefix is the parent directory path containing the file
                            prefix = clean_url_path.rsplit('/', 1)[0] + '/'

                        # Check if this S3 file is referenced by any OTHER active layer linked to a map
                        # We match by both the exact url_path and any of its sub-layer formats (using LIKE)
                        other_stmt = select(map_layer.c.map_id).join(
                            LayerEntity, map_layer.c.layer_id == LayerEntity.id
                        ).where(
                            and_(
                                or_(
                                    LayerEntity.url_path == clean_url_path,
                                    LayerEntity.url_path.like(clean_url_path + "|%")
                                ),
                                LayerEntity.bucket == db_layer.bucket
                            )
                        )
                        other_res = await session.execute(other_stmt)
                        other_map_id = other_res.scalars().first()
                        print(f"[delete_map] Checking other map usage for clean file '{clean_url_path}'... Found active map ID: {other_map_id}")
                        
                        if not other_map_id:
                            # Safe to physically delete from S3/MinIO
                            if prefix:
                                print(f"[delete_map] SAFE TO PURGE PREFIX: Recursive delete prefix '{prefix}' from bucket '{db_layer.bucket}'...")
                                self.minio_service.delete_prefix(prefix, bucket=db_layer.bucket)
                            else:
                                print(f"[delete_map] SAFE TO PURGE FILE: Single delete object '{clean_url_path}' from bucket '{db_layer.bucket}'...")
                                self.minio_service.delete_object(clean_url_path, bucket=db_layer.bucket)

                            # Clean up any leftover duplicate orphaned layer records referencing this file
                            orphan_stmt = select(LayerEntity).where(
                                and_(
                                    or_(
                                        LayerEntity.url_path == clean_url_path,
                                        LayerEntity.url_path.like(clean_url_path + "|%")
                                    ),
                                    LayerEntity.bucket == db_layer.bucket,
                                    LayerEntity.id != db_layer.id
                                )
                            )
                            orphan_res = await session.execute(orphan_stmt)
                            orphaned_layers = orphan_res.scalars().all()
                            for o_layer in orphaned_layers:
                                # Double check if it is truly an orphan (not linked to any map)
                                chk_stmt = select(map_layer.c.map_id).where(map_layer.c.layer_id == o_layer.id)
                                chk_res = await session.execute(chk_stmt)
                                if not chk_res.fetchall():
                                    print(f"[delete_map] Self-Healing: Deleting orphan layer record {o_layer.id} referencing '{clean_url_path}'")
                                    await session.delete(o_layer)
                        else:
                            print(f"[delete_map] Shared file '{clean_url_path}' still used by active map ID {other_map_id}. Skipping S3 deletion.")
                    
                    # Delete the layer record
                    await session.delete(db_layer)

            # 6. Delete the map itself
            await session.delete(db_map)
            
            # 7. Commit everything in a single, safe transaction
            await session.commit()
            return True

    async def get_maps_merged(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        collection_id: Optional[uuid.UUID] = None,
        tenant_id: str | None = None
    ) -> List[MergedMapResponse]:
        async with self.repo._db.session() as session:
            stmt = select(MapEntity)
            if tenant_id:
                stmt = stmt.where(MapEntity.tenant_id == tenant_id)
            if name:
                stmt = stmt.where(MapEntity.name.ilike(f"%{name}%"))
            if collection_id:
                stmt = stmt.join(
                    collection_map, MapEntity.id == collection_map.c.map_id
                ).where(
                    collection_map.c.collection_id == collection_id
                )
            
            stmt = stmt.offset(skip).limit(limit)
            res = await session.execute(stmt)
            maps = res.scalars().all()

            merged_results = []
            for map_obj in maps:
                c_stmt = select(CollectionEntity).join(
                    collection_map, CollectionEntity.id == collection_map.c.collection_id
                ).where(
                    collection_map.c.map_id == map_obj.id
                )
                c_res = await session.execute(c_stmt)
                collections = c_res.scalars().all()

                map_response = MapResponse.model_validate(map_obj)
                merged_map = MergedMapResponse(
                    **map_response.model_dump(),
                    collections=[CollectionResponse.model_validate(c) for c in collections],
                    layers=[]
                )
                merged_results.append(merged_map)

            return merged_results

    async def get_map_merged(self, map_id: uuid.UUID, tenant_id: str | None = None) -> MergedMapResponse:
        async with self.repo._db.session() as session:
            map_obj = await self.repo.get(map_id, tenant_id)
            if not map_obj:
                raise ValueError("Map not found")

            # Fetch collections
            c_stmt = select(CollectionEntity).join(
                collection_map, CollectionEntity.id == collection_map.c.collection_id
            ).where(
                collection_map.c.map_id == map_id
            )
            c_res = await session.execute(c_stmt)
            collections = c_res.scalars().all()

            # Fetch layers
            l_stmt = select(LayerEntity).join(
                map_layer, LayerEntity.id == map_layer.c.layer_id
            ).where(
                map_layer.c.map_id == map_id
            )
            l_res = await session.execute(l_stmt)
            layers = l_res.scalars().all()

            map_response = MapResponse.model_validate(map_obj)
            merged_map = MergedMapResponse(
                **map_response.model_dump(),
                collections=[CollectionResponse.model_validate(c) for c in collections],
                layers=[MergedLayerResponse.model_validate(l) for l in layers]
            )
            return merged_map

class LayerService(BaseEntityService[LayerRepository, LayerResponse, LayerCreate, LayerCreate, LayerCreate]):
    def __init__(self, async_db: AsyncDatabase, minio_service: MinioService) -> None:
        self.minio_service = minio_service
        super().__init__(async_db, LayerRepository, LayerResponse)

    async def create_layer(
        self,
        map_id: uuid.UUID,
        layer_data: LayerCreate,
        file_name: Optional[str] = None,
        file_data: Optional[bytes] = None,
        tenant_id: str | None = None,
        user_id: str | None = None
    ) -> LayerResponse:
        creator_id = user_id or "system"
        layer_id = uuid.uuid4()
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        t_lower = layer_data.type.lower()
        is_file_based = any(t_lower == ext or t_lower.endswith(ext) or ext.endswith(t_lower) for ext in LayerFileType)

        url_path = None
        bucket = None

        if is_file_based and file_data and file_name:
            if not file_name.lower().endswith(t_lower):
                raise ValueError("File format does not match the layer type")
            
            url_path = f"layers/{layer_id}/{file_name}"
            bucket = "desktop-mobile"

            if t_lower == ".geojson":
                resolver = GeoJSONConflictResolver()
                file_geojson = resolver.blob_to_geojson(file_data)
                file_geojson = resolver.add_guid_to_geojson(file_geojson)
                file_geojson = resolver.add_update_download_time(file_geojson)
                file_data = resolver.geojson_to_blob(file_geojson)
            
            elif t_lower == ".gpkg":
                resolver = GPKGConflictResolver()
                temp_dir = tempfile.mkdtemp()
                temp_gpkg_path = os.path.join(temp_dir, file_name)
                try:
                    with open(temp_gpkg_path, "wb") as f:
                        f.write(file_data)
                    
                    cls_names = resolver.get_gpkg_feature_classes(temp_gpkg_path)
                    for cls_name in cls_names:
                        resolver.setup_client_side_triggers(temp_gpkg_path, cls_name, creator_id)
                        resolver.add_update_download_time_to_gpkg(temp_gpkg_path, cls_name)
                    
                    try:
                        conn = sqlite3.connect(temp_gpkg_path)
                        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                        conn.execute("PRAGMA journal_mode=DELETE;")
                        conn.close()
                    except Exception as e:
                        print(f"Could not checkpoint WAL database: {e}")
                    
                    with open(temp_gpkg_path, "rb") as f:
                        file_data = f.read()
                finally:
                    if os.path.exists(temp_gpkg_path):
                        os.remove(temp_gpkg_path)
                    shutil.rmtree(temp_dir, ignore_errors=True)

            self.minio_service.put_object(url_path, file_data, bucket=bucket)
        elif is_file_based and not file_data:
            file_store_id = None
            if layer_data.route_params:
                for param in layer_data.route_params:
                    p_type = param.get("type", "").lower() if isinstance(param, dict) else (getattr(param, "type", "").lower() if hasattr(param, "type") else "")
                    p_route_id = param.get("route_id") if isinstance(param, dict) else (getattr(param, "route_id", None) if hasattr(param, "route_id") else None)
                    if p_type == "file" and p_route_id:
                        file_store_id = p_route_id
                        break
            
            if file_store_id:
                try:
                    from sqlalchemy import text
                    async with self.repo._db.session() as session:
                        query = text("SELECT file_url FROM spatial.file_store WHERE id = :fs_id")
                        result = await session.execute(query, {"fs_id": file_store_id})
                        row = result.first()
                        if row and row[0]:
                            url_path = row[0]
                            bucket = "mapa-spatial-files"
                            print(f"[LayerService] Linked spatial file_store {file_store_id} -> url_path='{url_path}' in bucket='{bucket}'")
                except Exception as e:
                    print(f"[LayerService] Failed to retrieve spatial file_store url: {e}")
            
            if not url_path:
                url_path = layer_data.url_path
                bucket = layer_data.bucket
        else:
            url_path = layer_data.url_path
            bucket = layer_data.bucket

        async with self.repo._db.session() as session:
            new_layer = LayerEntity(
                id=layer_id,
                name=layer_data.name,
                type=layer_data.type,
                tags=layer_data.tags,
                url_path=url_path,
                bucket=bucket,
                qml_params=layer_data.qml_params,
                sld_params=layer_data.sld_params,
                web_layer_definition_id=layer_data.web_layer_definition_id,
                creator=creator_id,
                updater=creator_id,
                created_at=now,
                updated_at=now,
                tenant_id=tenant_id
            )
            session.add(new_layer)
            await session.flush()

            if map_id:
                stmt = map_layer.insert().values(
                    map_id=map_id,
                    layer_id=layer_id
                )
                await session.execute(stmt)
            
            await session.commit()
            
        return await self.get(layer_id, tenant_id)

    async def update_layer(
        self,
        layer_id: uuid.UUID,
        layer_data: LayerCreate,
        file_name: Optional[str] = None,
        file_data: Optional[bytes] = None,
        tenant_id: str | None = None,
        user_id: str | None = None
    ) -> LayerResponse:
        updater_id = user_id or "system"
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        async with self.repo._db.session() as session:
            stmt = select(LayerEntity).where(LayerEntity.id == layer_id)
            if tenant_id:
                stmt = stmt.where(LayerEntity.tenant_id == tenant_id)
            res = await session.execute(stmt)
            updated_layer = res.scalars().first()
            
            if not updated_layer:
                raise ValueError(f"Layer not found: {layer_id}")

            t_lower = updated_layer.type.lower()
            is_file_based = any(t_lower == ext or t_lower.endswith(ext) or ext.endswith(t_lower) for ext in LayerFileType)

            is_data_source_changed = False
            conflicts_list = {}

            if is_file_based and file_data and file_name:
                if t_lower == ".gpkg":
                    if not file_name.lower().endswith(".json"):
                        raise ValueError("GeoPackage edits must be submitted in JSON Delta format")
                    
                    resolver = GPKGConflictResolver()
                    all_layer_data = json.loads(file_data.decode("utf-8"))
                    temp_dir = tempfile.mkdtemp()
                    temp_gpkg_path = os.path.join(temp_dir, f"{layer_id}.gpkg")
                    
                    try:
                        if updated_layer.url_path:
                            master_bytes = self.minio_service.get_object(updated_layer.url_path, bucket=updated_layer.bucket)
                            with open(temp_gpkg_path, "wb") as f:
                                f.write(master_bytes)
                        else:
                            raise ValueError("Master GPKG file does not exist on S3")

                        for cls_name, layer_payload in all_layer_data.items():
                            metadata = layer_payload.get("metadata", {})
                            user_changes = layer_payload.get("changes", [])
                            download_time = metadata.get("download_time")
                            
                            if not download_time:
                                continue

                            if user_changes:
                                db_gdfjson = resolver.gpkg_to_gdfjson(temp_gpkg_path, cls_name, False)
                                _, red_changes = resolver.reconstruct_to_time(db_gdfjson, download_time)
                                comparison = resolver.find_user_changes_with_conflicts(user_changes, red_changes)
                                resolver.add_changed_features_to_gpkg(temp_gpkg_path, cls_name, comparison, updater_id)

                                if comparison.get("conflicts"):
                                    conflicts_list[cls_name] = {"conflicts": comparison["conflicts"]}

                        try:
                            conn = sqlite3.connect(temp_gpkg_path)
                            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                            conn.execute("PRAGMA journal_mode=DELETE;")
                            conn.close()
                        except Exception as e:
                            print(f"Could not checkpoint WAL GPKG: {e}")

                        with open(temp_gpkg_path, "rb") as f:
                            resolved_gpkg_bytes = f.read()
                        self.minio_service.put_object(updated_layer.url_path, resolved_gpkg_bytes, bucket=updated_layer.bucket)
                        is_data_source_changed = True
                    finally:
                        if os.path.exists(temp_gpkg_path):
                            os.remove(temp_gpkg_path)
                        shutil.rmtree(temp_dir, ignore_errors=True)

                elif t_lower == ".geojson":
                    if not file_name.lower().endswith(".geojson"):
                        raise ValueError("File format does not match with geojson")
                    
                    resolver = GeoJSONConflictResolver()
                    user_geojson = resolver.blob_to_geojson(file_data)
                    user_geojson = resolver.add_guid_to_geojson(user_geojson)
                    download_time = resolver.extract_download_time(user_geojson)
                    
                    temp_dir = tempfile.mkdtemp()
                    try:
                        if updated_layer.url_path:
                            master_bytes = self.minio_service.get_object(updated_layer.url_path, bucket=updated_layer.bucket)
                            db_geojson = resolver.blob_to_geojson(master_bytes)
                        else:
                            raise ValueError("Master GeoJSON file does not exist on S3")

                        downloaded_features, red_changes = resolver.reconstruct_to_time(db_geojson, download_time)
                        new_features = user_geojson.get('features', [])
                        comparison = resolver.find_changes_with_conflicts(downloaded_features, new_features, red_changes)
                        
                        db_geojson = resolver.add_changed_features(db_geojson, comparison, updater_id)
                        resolved_json_bytes = resolver.geojson_to_blob(db_geojson)
                        self.minio_service.put_object(updated_layer.url_path, resolved_json_bytes, bucket=updated_layer.bucket)
                        is_data_source_changed = True
                    finally:
                        shutil.rmtree(temp_dir, ignore_errors=True)

                else:
                    if not file_name.lower().endswith(t_lower):
                        raise ValueError("File format does not match the layer type")
                    if not updated_layer.url_path:
                        updated_layer.url_path = f"layers/{layer_id}/{file_name}"
                    
                    self.minio_service.put_object(updated_layer.url_path, file_data, bucket=updated_layer.bucket)
                    is_data_source_changed = True

            update_data = layer_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key in ("url_path", "qml_params", "sld_params"):
                    continue
                setattr(updated_layer, key, value)

            if layer_data.url_path:
                if not (t_lower in (".gpkg", ".geojson")):
                    updated_layer.url_path = layer_data.url_path

            if layer_data.qml_params:
                if field_changed(normalize_qml(updated_layer.qml_params), normalize_qml(layer_data.qml_params)):
                    updated_layer.qml_params = layer_data.qml_params
                    updated_layer.sld_params = layer_data.sld_params
                    updated_layer.updater = updater_id
                    updated_layer.updated_at = now

            if is_data_source_changed:
                if updated_layer.url_path:
                    # 1. Update the active layer's fields normally
                    updated_layer.created_at = now
                    updated_layer.updater = updater_id
                    updated_layer.updated_at = now
                    
                    # 2. Update ONLY created_at on all other layers sharing the same path to notify data change
                    from sqlalchemy import update as sqlalchemy_update
                    upd_stmt = sqlalchemy_update(LayerEntity).where(
                        and_(
                            LayerEntity.url_path == updated_layer.url_path,
                            LayerEntity.bucket == updated_layer.bucket,
                            LayerEntity.id != updated_layer.id
                        )
                    ).values(
                        created_at=now
                    )
                    await session.execute(upd_stmt)
                else:
                    updated_layer.created_at = now
                    updated_layer.updater = updater_id
                    updated_layer.updated_at = now

            await session.commit()
            
            layer_res = await self.get(layer_id, tenant_id)
            if conflicts_list and layer_res:
                layer_res.conflicts_list = conflicts_list
                
            return layer_res

    async def delete_layer(self, layer_id: uuid.UUID, tenant_id: str | None = None) -> bool:
        async with self.repo._db.session() as session:
            stmt = select(LayerEntity).where(LayerEntity.id == layer_id)
            if tenant_id:
                stmt = stmt.where(LayerEntity.tenant_id == tenant_id)
            res = await session.execute(stmt)
            db_layer = res.scalars().first()
            
            if not db_layer:
                raise ValueError("Layer not found")

            # Safe cleanup: check if the same S3 file is referenced by any other layer row linked to an active map
            if db_layer.url_path:
                clean_url_path = db_layer.url_path.split('|')[0]
                prefix = None
                if '/' in clean_url_path:
                    prefix = clean_url_path.rsplit('/', 1)[0] + '/'

                other_stmt = select(map_layer.c.map_id).join(
                    LayerEntity, map_layer.c.layer_id == LayerEntity.id
                ).where(
                    and_(
                        or_(
                            LayerEntity.url_path == clean_url_path,
                            LayerEntity.url_path.like(clean_url_path + "|%")
                        ),
                        LayerEntity.bucket == db_layer.bucket,
                        map_layer.c.layer_id != layer_id
                    )
                )
                other_res = await session.execute(other_stmt)
                other_map_id = other_res.scalars().first()
                
                if not other_map_id:
                    # No other active map references this S3 object, safe to delete physically
                    if prefix:
                        self.minio_service.delete_prefix(prefix, bucket=db_layer.bucket)
                    else:
                        self.minio_service.delete_object(clean_url_path, bucket=db_layer.bucket)

                    # Clean up any leftover duplicate orphaned layer records referencing this file
                    orphan_stmt = select(LayerEntity).where(
                        and_(
                            or_(
                                LayerEntity.url_path == clean_url_path,
                                LayerEntity.url_path.like(clean_url_path + "|%")
                            ),
                            LayerEntity.bucket == db_layer.bucket,
                            LayerEntity.id != layer_id
                        )
                    )
                    orphan_res = await session.execute(orphan_stmt)
                    orphaned_layers = orphan_res.scalars().all()
                    for o_layer in orphaned_layers:
                        # Double check if it is truly an orphan (not linked to any map)
                        chk_stmt = select(map_layer.c.map_id).where(map_layer.c.layer_id == o_layer.id)
                        chk_res = await session.execute(chk_stmt)
                        if not chk_res.fetchall():
                            await session.delete(o_layer)
                else:
                    print(f"[LayerService] S3 file '{clean_url_path}' is still referenced by other active maps (e.g. Map ID: {other_map_id}). Skipping physical deletion.")

            rel_stmt = delete(map_layer).where(map_layer.c.layer_id == layer_id)
            await session.execute(rel_stmt)

            await session.delete(db_layer)
            await session.commit()
            return True

class ApiKeyService(BaseEntityService[ApiKeyRepository, ApiKeyResponse, ApiKeyCreate, ApiKeyCreate, ApiKeyCreate]):
    def __init__(self, async_db: AsyncDatabase, permission_repo: ApiKeyPermissionRepository) -> None:
        self.permission_repo = permission_repo
        super().__init__(async_db, ApiKeyRepository, ApiKeyResponse)

    async def generate_key(self, description: Optional[str], expires_at: datetime, tenant_id: str | None = None, is_first: bool = False) -> Dict[str, Any]:
        """Generates a cryptographically secure API Key, hashes it, and saves it."""
        raw_key, public_lookup_id, hashed_key = generate_key_data()
        
        key_dict = {
            "public_lookup_id": public_lookup_id,
            "hashed_key": hashed_key,
            "description": description,
            "is_active": True,
            "expires_at": expires_at
        }
        
        db_key = await self.repo.create(key_dict, tenant_id, "admin")
        
        if is_first:
            perm_dict = {
                "apikey_id": db_key.id,
                "target_collection_id": None,
                "target_map_id": None,
                "target_layer_id": None,
                "access_level": ResourceAccess.ADMIN.value
            }
            await self.permission_repo.create(perm_dict, tenant_id, "admin")

        key_response = self.model_type.model_validate(self.repo.dict(db_key))
        
        return {
            "raw_secret_key": raw_key,
            "api_key_record": key_response
        }

class ApiKeyPermissionService(BaseEntityService[ApiKeyPermissionRepository, ApiKeyPermissionResponse, ApiKeyPermissionCreate, ApiKeyPermissionCreate, ApiKeyPermissionCreate]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ApiKeyPermissionRepository, ApiKeyPermissionResponse)
