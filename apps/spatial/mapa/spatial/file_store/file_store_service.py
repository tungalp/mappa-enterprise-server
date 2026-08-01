from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.file_store.file_store_model import CreateFileStore, UpdateAllFileStore, UpdateFileStore, FileStore
from mapa.spatial.file_store.file_store_repository import FileStoreRepository
from mapa.core.data.query_args import QueryArgs


import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import hashlib
import copy
import uuid
import base64


class FileStoreService(BaseEntityService[FileStoreRepository, FileStore, CreateFileStore, UpdateFileStore, UpdateAllFileStore]):
    """FileStore Servisi"""

    def __init__(self, async_db: AsyncDatabase, minio_service: Any = None) -> None:
        super().__init__(async_db, FileStoreRepository, FileStore)
        self.minio_service = minio_service

    async def delete(self, obj_id: Any, tenant_id: str | None = None) -> bool:
        item = await self.get(obj_id, tenant_id)
        if item and item.file_url and self.minio_service:
            self.minio_service.delete_object(item.file_url)
        return await super().delete(obj_id, tenant_id)

    async def delete_by_ids(self, obj_ids: List[Any], tenant_id: str | None = None) -> int:
        for obj_id in obj_ids:
            item = await self.get(obj_id, tenant_id)
            if item and item.file_url and self.minio_service:
                self.minio_service.delete_object(item.file_url)
        return await super().delete_by_ids(obj_ids, tenant_id)

    async def delete_all(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        items = await self.find(query_args, tenant_id)
        if items:
            for item in items:
                if item.file_url and self.minio_service:
                    self.minio_service.delete_object(item.file_url)
        return await super().delete_all(query_args, tenant_id)

    async def list_gdb_layers(self, file_store_id: str, tenant_id: str | None = None) -> List[Dict[str, Any]]:
        import tempfile
        import zipfile
        import io
        import os
        import fiona
        import fiona.drvsupport

        fiona.drvsupport.supported_drivers['KML'] = 'r'
        fiona.drvsupport.supported_drivers['LIBKML'] = 'r'
        fiona.drvsupport.supported_drivers['KMZ'] = 'r'
        fiona.drvsupport.supported_drivers['PGeo'] = 'r'
        fiona.drvsupport.supported_drivers['MDB'] = 'r'
        
        file_store = await self.get(file_store_id, tenant_id)
        if not file_store:
            raise Exception("FileStore not found")
            
        if not file_store.file_url:
            raise Exception("FileStore URL is empty")
            
        object_name = file_store.file_url
        file_bytes = self.minio_service.get_object(object_name)
        
        temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as z:
                z.extractall(temp_dir)
                
            gdb_path = None
            for root, dirs, files in os.walk(temp_dir):
                for d in dirs:
                    if d.lower().endswith(".gdb"):
                        gdb_path = os.path.join(root, d)
                        break
                if gdb_path:
                    break
                    
            if not gdb_path:
                raise Exception("Could not find .gdb folder inside zip.")
                
            layers = fiona.listlayers(gdb_path)
            
            result = []
            # Priority order for auto-detecting numeric key field
            KEY_FIELD_CANDIDATES = ["objectid", "objectid_1", "fid", "fid_1", "id"]

            for idx, lyr in enumerate(sorted(layers)):
                # Read layer schema to auto-detect key field and geometry type
                key_field = None
                geometry_type = "Geometry"
                try:
                    with fiona.open(gdb_path, layer=lyr) as src:
                        schema_props = src.schema.get("properties", {})
                        geom = src.schema.get("geometry", "Geometry")
                        if geom:
                            geometry_type = geom

                        # Collect integer fields (int, int32, int64)
                        int_fields = {
                            k.lower(): k
                            for k, v in schema_props.items()
                            if isinstance(v, str) and v.lower() in ("int", "int32", "int64", "integer", "long")
                        }

                        # Find any integer field starting with 'objectid'
                        objectid_fields = [v for k, v in int_fields.items() if k.startswith("objectid")]
                        if objectid_fields:
                            # Prefer exact 'objectid' if exists, else first one like 'objectid_1'
                            exact = [f for f in objectid_fields if f.lower() == "objectid"]
                            key_field = exact[0] if exact else objectid_fields[0]
                        else:
                            # Fallback to other candidates if no objectid variant exists
                            for candidate in KEY_FIELD_CANDIDATES:
                                if candidate in int_fields:
                                    key_field = int_fields[candidate]
                                    break

                            # Fallback: first integer field found
                            if not key_field and int_fields:
                                key_field = next(iter(int_fields.values()))

                            # User requested strict fallback to 'OBJECTID' for GDB if all else fails
                            if not key_field:
                                key_field = "OBJECTID"
                except Exception:
                    pass  # schema read failure is non-fatal

                type_name = f"file:{lyr}"
                result.append({
                    "id": f"{file_store_id}|{lyr}",
                    "key": f"gdb_layer_{idx}",
                    "title": lyr,
                    "code": lyr,
                    "name": lyr,
                    "isLeaf": True,
                    "is_base_layer": False,
                    "data_type": "file",
                    "key_field": key_field,
                    "type_name": type_name,
                    "target_namespace": "file",
                    "geometry_field_param": {
                        "type": geometry_type,
                        "srid": "EPSG:4326",
                        "field_name": "shape",
                    },
                    "children": []
                })

            return result
        except Exception as e:
            import logging
            logging.error(f"Error in list_gdb_layers: {str(e)}", exc_info=True)
            raise e
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def get_file_schema(self, file_store_id: str, tenant_id: str | None = None) -> Dict[str, Any]:
        """
        Returns field names/types and an auto-detected key_field for any supported file type.
        Supports GeoJSON (JSON parsing) and KML/KMZ/SHP/GPKG etc. (via fiona).
        Key field priority: OBJECTID -> OBJECTID_1 -> FID -> FID_1 -> ID -> first integer -> first field.
        """
        import json as _json
        import tempfile
        import io
        import os

        KEY_FIELD_CANDIDATES = ["objectid", "objectid_1", "fid", "fid_1", "id"]

        file_store = await self.get(file_store_id, tenant_id)
        if not file_store:
            raise Exception("FileStore not found")
        if not file_store.file_url:
            raise Exception("FileStore has no file associated")

        file_format = (file_store.file_format or "").lower()

        raw_bytes = self.minio_service.get_object(file_store.file_url)
        if not raw_bytes:
            raise Exception("File is empty or missing in storage")

        def _auto_select_key(int_fields: Dict[str, str], all_fields: list) -> str | None:
            """Pick best integer key field using priority candidates."""
            objectid_fields = [v for k, v in int_fields.items() if k.startswith("objectid")]
            if objectid_fields:
                exact = [f for f in objectid_fields if f.lower() == "objectid"]
                return exact[0] if exact else objectid_fields[0]

            for candidate in KEY_FIELD_CANDIDATES:
                if candidate in int_fields:
                    return int_fields[candidate]
            if int_fields:
                return next(iter(int_fields.values()))
            
            # Strict fallback to 'OBJECTID' if nothing matches
            return "OBJECTID"

        # ── GeoJSON: inspect property values from first feature ──────────────
        if file_format in (".geojson", "geojson"):
            try:
                geojson = _json.loads(raw_bytes.decode("utf-8"))
            except Exception as e:
                raise Exception(f"Could not parse GeoJSON: {e}")

            features = geojson.get("features", [])
            if not features:
                return {"key_field": None, "fields": []}

            props = features[0].get("properties", {}) or {}
            fields = []
            int_fields: Dict[str, str] = {}

            for field_name, value in props.items():
                if isinstance(value, bool):
                    field_type = "boolean"
                elif isinstance(value, int):
                    field_type = "integer"
                    int_fields[field_name.lower()] = field_name
                elif isinstance(value, float):
                    field_type = "float"
                else:
                    field_type = "string"
                fields.append({"name": field_name, "type": field_type})

            return {"key_field": _auto_select_key(int_fields, fields), "fields": fields}

        # ── Fiona-readable formats: KML, KMZ, SHP, GPKG etc. ─────────────────
        FIONA_FORMATS = {".kml", ".kmz", ".shp.zip", ".gpkg", ".mdb"}
        if file_format in FIONA_FORMATS or file_format.endswith((".kml", ".kmz")):
            import fiona
            import fiona.drvsupport
            fiona.drvsupport.supported_drivers['KML'] = 'r'
            fiona.drvsupport.supported_drivers['LIBKML'] = 'r'
            fiona.drvsupport.supported_drivers['KMZ'] = 'r'

            temp_dir = tempfile.mkdtemp()
            try:
                # Write raw bytes to a temp file with correct extension
                ext = file_format if file_format.startswith(".") else f".{file_format}"
                temp_file = os.path.join(temp_dir, f"file{ext}")
                with open(temp_file, "wb") as f:
                    f.write(raw_bytes)

                # Read first layer's schema
                layers = fiona.listlayers(temp_file)
                if not layers:
                    return {"key_field": None, "fields": []}

                fields = []
                int_fields: Dict[str, str] = {}
                FIONA_INT_TYPES = ("int", "int32", "int64", "integer", "long")

                with fiona.open(temp_file, layer=layers[0]) as src:
                    for fname, ftype in src.schema.get("properties", {}).items():
                        ftype_str = str(ftype).lower()
                        if ftype_str in FIONA_INT_TYPES:
                            fields.append({"name": fname, "type": "integer"})
                            int_fields[fname.lower()] = fname
                        elif "float" in ftype_str or "double" in ftype_str or "real" in ftype_str:
                            fields.append({"name": fname, "type": "float"})
                        else:
                            fields.append({"name": fname, "type": "string"})

                return {"key_field": _auto_select_key(int_fields, fields), "fields": fields}
            except Exception as e:
                import logging
                logging.warning(f"get_file_schema fiona read failed for {file_format}: {e}")
                return {"key_field": None, "fields": []}
            finally:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

        # ── Unsupported format: return safe default (frontend falls back to "objectid") ──
        return {"key_field": None, "fields": []}


    async def get_gdb_layer_geojson(self, file_store_id: str, layer_name: str, tenant_id: uuid.UUID | str = None) -> dict:
        """
        Extracts the .gdb.zip file, reads the specified layer, and converts it to GeoJSON.
        """

        import tempfile
        import zipfile
        import io
        import os
        import fiona
        import geopandas as gpd
        import pandas as pd

        file_store = await self.get(file_store_id, tenant_id)
        if not file_store:
            raise Exception("File store not found")

        if not file_store.file_url:
            raise Exception("File store has no file associated")

        file_bytes = self.minio_service.get_object(file_store.file_url)
        if not file_bytes:
            raise Exception("File is empty or missing in storage")

        temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as z:
                z.extractall(temp_dir)
                
            gdb_path = None
            for root, dirs, files in os.walk(temp_dir):
                for d in dirs:
                    if d.lower().endswith(".gdb"):
                        gdb_path = os.path.join(root, d)
                        break
                if gdb_path:
                    break
                    
            if not gdb_path:
                raise Exception("Could not find .gdb folder inside zip.")
                
            gdf = gpd.read_file(gdb_path, layer=layer_name)
            
            if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            for col in gdf.columns:
                if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                    gdf[col] = gdf[col].apply(lambda val: val.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(val) else None)

            import json
            geojson_str = gdf.to_json()
            geojson_data = json.loads(geojson_str)
            return geojson_data
            
        except Exception as e:
            import logging
            logging.error(f"Error in get_gdb_layer_geojson: {str(e)}", exc_info=True)
            raise e
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)



class GeoJSONConflictResolver:
    row_guid = "row_guid"
    
    exclude_fields = [
        'last_updated', 'download_time', 'processing_timestamp', 
        'row_id', 'created_at', 'modified_at', 'updated_at',
        'timestamp', 'sync_time', 'import_date'
    ]
    
    def __init__(self):
        self.change_history = []
    
    def load_geojson(self, file_path: str) -> Dict[str, Any]:
        """Load GeoJSON from file"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def save_geojson(self, data: Dict[str, Any], file_path: str):
        """Save GeoJSON to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def add_update_download_time(self, geojson_data):
        """
        Add download_time to GeoJSON when user downloads data
        """
        # Add current time as download_time
        current_time = datetime.now().isoformat()
        
        # Make sure properties exists
        if 'metadata' not in geojson_data:
            geojson_data['metadata'] = {}
        
        # Add download_time
        geojson_data['metadata']['download_time'] = current_time
        
        return geojson_data

    def add_guid_to_geojson(self, geojson: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Adds id to GeoJSON features if it doesn't exist.        
        """
        
        # Handle string input (JSON)
        if isinstance(geojson, str):
            try:
                geojson = json.loads(geojson)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")
        
        # Validate input
        if not isinstance(geojson, dict):
            raise TypeError("Input must be a dictionary or valid JSON string")
        
        # Check if it's a valid GeoJSON structure
        if 'type' not in geojson:
            raise ValueError('Invalid GeoJSON: missing "type" property')
        
        # Create a copy to avoid modifying the original
        result = geojson.copy()
        
        # Handle FeatureCollection
        if result['type'] == 'FeatureCollection':
            if 'features' not in result or not isinstance(result['features'], list):
                raise ValueError('Invalid GeoJSON FeatureCollection: missing or invalid "features" array')
            
            # Process each feature
            result['features'] = [self.add_guid_to_feature(feature) for feature in result['features']]
        
        # Handle single Feature
        elif result['type'] == 'Feature':
            result = self.add_guid_to_feature(result)
        
        else:
            # For other GeoJSON types (Point, LineString, etc.), return as-is
            # These don't have properties where we can add id
            pass
        return result
    
    def add_guid_to_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single GeoJSON feature, adding id if needed.
        """       
        # Validate feature structure
        if not isinstance(feature, dict):
            raise ValueError("Feature must be a dictionary")
        # Create a copy of the feature
        processed_feature = feature.copy()
        
        # Add id if it doesn't exist
        if self.row_guid not in processed_feature:
            processed_feature[self.row_guid] = str(uuid.uuid4())
        return processed_feature

    def base64_to_geojson(self, base64_data: str) -> Dict[str, Any]:
        """
        Convert base64 encoded data back to GeoJSON.
        """
        
        try:
            # Decode base64 to bytes
            decoded_bytes = base64.b64decode(base64_data)
            
            # Convert bytes to string (assuming UTF-8 encoding)
            json_string = decoded_bytes.decode('utf-8')
            
            # Parse JSON string to dictionary
            geojson_data = json.loads(json_string)
            
            # Basic GeoJSON validation
            if not isinstance(geojson_data, dict):
                raise ValueError("Decoded data is not a valid JSON object")
                
            if 'type' not in geojson_data:
                raise ValueError("Missing 'type' field - not a valid GeoJSON")
                
            return geojson_data
            
        except base64.binascii.Error as e:
            raise ValueError(f"Invalid base64 data: {e}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Cannot decode bytes to UTF-8: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")

    def geojson_to_base64(self, geojson_data: Dict[str, Any]) -> bytes:
        """
        Convert GeoJSON data to base64 encoded bytes.
        """
        
        try:
            # Basic GeoJSON validation
            if not isinstance(geojson_data, dict):
                raise ValueError("Input data is not a valid dictionary object")
                
            if 'type' not in geojson_data:
                raise ValueError("Missing 'type' field - not a valid GeoJSON")
            
            # Convert dictionary to JSON string
            json_string = json.dumps(geojson_data, separators=(',', ':'))
            
            # Convert string to bytes (UTF-8 encoding)
            json_bytes = json_string.encode('utf-8')
            
            # Encode bytes to base64, directly write byte data if you want string .decode('utf-8')
            base64_data = base64.b64encode(json_bytes)
            
            return base64_data
            
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot serialize GeoJSON to JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error encoding to base64: {e}")
        
    def validate_geojson(self, geojson: Dict[str, Any]) -> bool:
        """
        Validate if the decoded data is a proper GeoJSON.
        
        Args:
            geojson: Dictionary to validate
            
        Returns:
            bool: True if valid GeoJSON structure
        """
        
        if not isinstance(geojson, dict):
            return False
            
        geojson_type = geojson.get('type')
        
        # Check valid GeoJSON types
        valid_types = ['FeatureCollection', 'Feature', 'Point', 'LineString', 
                    'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon', 
                    'GeometryCollection']
        
        if geojson_type not in valid_types:
            return False
            
        # Additional validation for FeatureCollection
        if geojson_type == 'FeatureCollection':
            if 'features' not in geojson or not isinstance(geojson['features'], list):
                return False
                
        # Additional validation for Feature
        elif geojson_type == 'Feature':
            required_keys = ['properties', 'geometry']
            if not all(key in geojson for key in required_keys):
                return False
                
        return True

    def validate_geojson_structure(self, geojson: Dict[str, Any]) -> bool:
        """
        Validate if a GeoJSON object has the expected structure.
        """
        
        try:
            if geojson.get('type') == 'FeatureCollection':
                if 'features' not in geojson or not isinstance(geojson['features'], list):
                    return False
                
                for feature in geojson['features']:
                    if not self._is_valid_feature(self, feature):
                        return False
                        
            elif geojson.get('type') == 'Feature':
                return self._is_valid_feature(self, geojson)
                
            return True
            
        except Exception:
            return False

    def _is_valid_feature(self, feature: Dict[str, Any]) -> bool:
        """
        Check if a feature has valid GeoJSON structure.
        """
        
        if not isinstance(feature, dict):
            return False
            
        required_keys = ['type', 'properties', 'geometry']
        
        # Check required keys exist
        if not all(key in feature for key in required_keys):
            return False
            
        # Check type is 'Feature'
        if feature['type'] != 'Feature':
            return False
            
        # Properties can be dict or None
        if feature['properties'] is not None and not isinstance(feature['properties'], dict):
            return False
            
        # Geometry should be dict or None
        if feature['geometry'] is not None and not isinstance(feature['geometry'], dict):
            return False
            
        return True

    def extract_download_time(self, geojson_data: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract download_time from GeoJSON properties or features
        """
        # Check if download_time is in main properties
        if 'metadata' in geojson_data and 'download_time' in geojson_data['metadata']:
            return datetime.fromisoformat(geojson_data['metadata']['download_time'])
        
        # Check if download_time is in first feature (common pattern)
        if 'features' in geojson_data and len(geojson_data['features']) > 0:
            first_feature = geojson_data['features'][0]
            if 'properties' in first_feature and 'download_time' in first_feature['properties']:
                return datetime.fromisoformat(first_feature['properties']['download_time'])
        
        return datetime.now()
    
    def find_feature_by_id(self, geojson_data: Dict[str, Any], object_id: Any) -> Optional[Dict[str, Any]]:
        """
        Find a feature by its object ID
        """
        for feature in geojson_data['features']:
            if feature.get(self.row_guid) == object_id:
                return feature
        return None

    def normalize_coordinates(self, coords, precision: int = 6):
        """
        Normalize coordinate precision for consistent comparison
        """
        if isinstance(coords, list):
            if isinstance(coords[0], (int, float)):
                # Single coordinate pair [lon, lat] or [lon, lat, elevation]
                return tuple(float(round(c, precision)) for c in coords)
            else:
                # Nested coordinates
                return tuple(self.normalize_coordinates(c, precision) for c in coords)
        return coords

    def get_geometry_hash(self, feature: Dict[str, Any]) -> str:
        """
        Generate a coordinate-based key for feature identification
        """
        geometry = feature.get('geometry', {})
        coords = geometry.get('coordinates')
        
        if not coords:
            return None
            
        # Normalize coordinates
        normalized_coords = self.normalize_coordinates(coords)
        
        # Create key from geometry type + coordinates
        geom_type = geometry.get('type', '')
        coord_str = json.dumps(normalized_coords, separators=(',', ':'))
        coord_key = f"{geom_type}:{coord_str}"

        return hashlib.sha256(coord_key.encode('utf-8')).hexdigest()
    
    def get_attribute_values(self, feature: Dict[str, Any], 
                          exclude_fields: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Prepare attribute list to compare.
        """
        if exclude_fields is None:
            exclude_fields = []
            
        # Create attribute list - initialize properties as dict, not string
        attribute_values = {
            # 'type': feature['type'], 
            # 'id': feature['type']
        }

        # Include filtered properties
        if 'properties' in feature and isinstance(feature['properties'], dict):
            for attribute in feature['properties']:
                if attribute not in exclude_fields:
                    attribute_values[attribute] = feature['properties'][attribute]

        return attribute_values 

    def get_properties_hash(self, feature: Dict[str, Any], 
                          exclude_fields: List[str] = None) -> str:
        """
        Generate SHA256 hash for GeoJSON feature based on type, id, geometry, and properties
        """
        if exclude_fields is None:
            exclude_fields = []
            
        # Get attribute list
        attribute_values = self.get_attribute_values(feature, exclude_fields)  # Fixed: removed self parameter
        
        # Convert to JSON string with consistent ordering
        feature_str = json.dumps(attribute_values, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA256 hash
        return hashlib.sha256(feature_str.encode('utf-8')).hexdigest()

    def add_changed_features(self, db_geojson: Dict[str, Any], comparison: Dict[str, Any], userid: str) -> Dict[str, Any]:
        """
        Add changed features to db_geojson under timestamp -> user_id structure.
        """
        
        # Initialize changed_features key if it doesn't exist
        if 'changes' not in db_geojson:
            db_geojson['changes'] = {}
                    
        # Initialize timestamp key if it doesn't exist
        current_timestamp = datetime.now().isoformat()
        if current_timestamp not in db_geojson['changes']:
            db_geojson['changes'][current_timestamp] = {}  
        
        # Add under timestamp -> userid
        db_geojson['changes'][current_timestamp]['userid'] = userid
        db_geojson['changes'][current_timestamp]['changed_features'] = comparison['changed_features']
        
        return db_geojson

    def sort_by_date_keys(self, data_dict, reverse=False):
        """Sort dictionary by date string keys"""
        return sorted(data_dict.items(), 
                    key=lambda x: datetime.fromisoformat(x[0].replace('Z', '+00:00')), 
                    reverse=reverse)

    def reconstruct_to_time(self, db_geojson: Dict[str, Any], download_time: datetime) -> List[str]:
        """
        Reconstruct original GeoJSON data at a specific point in time by applying changes in timelined changed_features dicts.
        """
        # Check download time
        if download_time is None:
            download_time = datetime.now()
              
        # Process change history to reconstruct original state
        changed_actions = db_geojson.get('changes', {})
        
        # After download_time is red, before is green change area
        green_changes= {}
        red_changes= {}
        
        # Copy to change for green area updates
        downloaded_features = {}
        if "features" in db_geojson:
            downloaded_features = copy.deepcopy(db_geojson["features"])
        
        for timestamp_str, change_group in self.sort_by_date_keys(changed_actions):
            try:
                # Parse timestamp (assuming ISO format like "2023-10-20T09:15:30")
                upload_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    
                userid = change_group.get('userid')
                changed_features = change_group.get('changed_features', [])
                
                # Process each diff in this timestamp
                for change in changed_features:
                    row_guid = change.get(self.row_guid)
                    change_type = change.get('change_type')  # 'update', 'insert', 'delete'
                    geometry = change.get('geometry', {})
                    properties = change.get('properties', {})

                    
                    # Initialize tracking for red area
                    if upload_time > download_time:
                        if row_guid not in red_changes:
                            red_changes[row_guid] = {
                                'change_type': change_type,
                                'geometry': {},
                                'properties': {},
                                'timestamp': upload_time,
                                'userid': userid
                            }

                        # For each changed geometry, keep only the LAST change after target_time
                        for attr_name, change_detail in geometry.items():
                            red_changes[row_guid]['geometry'][attr_name] = {
                                'new_value': change_detail.get('new_value'),
                                'change_type': change_type,
                                'timestamp': upload_time,
                                'userid': userid
                            }

                        # For each changed attribute, keep only the LAST change after target_time
                        for attr_name, change_detail in properties.items():
                            red_changes[row_guid]['properties'][attr_name] = {
                                'new_value': change_detail.get('new_value'),
                                'change_type': change_type,
                                'timestamp': upload_time,
                                'userid': userid
                            }

                    # Initialize tracking for green area
                    else:
                        green_changes[row_guid] = {
                            'change_type': change_type,
                            'geometry': {},
                            'properties': {}
                        }

                        # For each changed geometry, keep only the LAST change after target_time
                        for attr_name, change_detail in geometry.items():
                            green_changes[row_guid]['geometry'][attr_name] = {
                                'new_value': change_detail.get('new_value'),
                                'change_type': change_type
                            }

                        # For each changed attribute, keep only the LAST change after target_time
                        for attr_name, change_detail in properties.items():
                            green_changes[row_guid]['properties'][attr_name] = {
                                'new_value': change_detail.get('new_value'),
                                'change_type': change_type,
                            }

                        # Insert feature
                        if change_type == 'insert':
                            reconstructed_feature = {
                                'type': 'Feature',
                                'row_guid': row_guid,
                                'geometry': {},
                                'properties': {}
                            }
                            
                            for key, value in geometry.items():
                                reconstructed_feature['geometry'][key] = value['new_value']
                            for key, value in properties.items():
                                reconstructed_feature['properties'][key] = value['new_value']

                            # Adding new feature
                            downloaded_features.append(reconstructed_feature)

                        # Update feature
                        elif change_type == 'update':
                            for i, feature in enumerate(downloaded_features):
                                if feature.get('row_guid') == row_guid:

                                    for key, value in geometry.items():
                                        feature['geometry'][key] = value['new_value']
                                    for key, value in properties.items():
                                        feature['properties'][key] = value['new_value']

                        # Remove feature by row_guid directly from list
                        elif change_type == 'delete':

                            for i, feature in enumerate(downloaded_features):
                                if feature.get('row_guid') == row_guid:
                                    del downloaded_features[i]

            except:
                # Skip invalid timestamps
                continue

        return downloaded_features, red_changes
    
    # Compare features that is not changed after new_features' download_time (green area) and is changed after download_time (red area)
    def merge_changes_with_conflicts(self, downloaded_features: Dict[str, Any], 
                               new_features: Dict[str, Any], red_changes:List[str]) -> Dict[str, Any]:
        """
        Compare two GeoJSON files and identify changes
        
        Returns:
            Dict with:
            - unchanged_features: Features that haven't changed
            - changed_features: Features that have changed with change details
            - conflicts: Changed after download time user on same attribute
        """
        result = {
            'unchanged_features': [],
            'changed_features': [],
            'conflicts': []
        }
        
        # Create maps using coordinate keys
        exclude_fields = self.exclude_fields
        old_features_map = {}
        for f in downloaded_features:
            if self.row_guid not in f:
                f[self.row_guid] = str(uuid.uuid4())
            geometry_hash = self.get_geometry_hash(f)
            properties_hash = self.get_properties_hash(f, exclude_fields)
            f['geometry_hash'] = geometry_hash
            f['properties_hash'] = properties_hash
            old_features_map[f[self.row_guid]] = f
        
        new_features_map = {}
        for f in new_features:
            geometry_hash = self.get_geometry_hash(f)
            properties_hash = self.get_properties_hash(f, exclude_fields)
            f['geometry_hash'] = geometry_hash
            f['properties_hash'] = properties_hash
            new_features_map[f[self.row_guid]] = f
        
        # Check all features in the new GeoJSON
        for row_guid, new_feature in new_features_map.items():
            if row_guid in old_features_map:

                # Feature exists at same coordinates
                old_feature = old_features_map[row_guid]

                # Check all properties are same or not with hash
                new_properties_hash = new_feature['properties_hash']
                old_properties_hash = old_feature['properties_hash']
                new_geometry_hash = new_feature['geometry_hash']
                old_geometry_hash = old_feature['geometry_hash']

                # This feature has changes
                change_details = {
                    'row_guid': row_guid,
                    'change_type': 'update',
                    'geometry': {},
                    'properties': {},
                }

                # This feature has changes
                conflict_details = {
                    'row_guid': row_guid,
                    'change_type': 'update',
                    'geometry': {},
                    'properties': {},
                }

                # If all are same
                if (new_properties_hash == old_properties_hash and new_geometry_hash == old_geometry_hash):
                    result['unchanged_features'].append(row_guid)
                    continue

                # If attributes are different
                if (new_properties_hash != old_properties_hash):

                    # There is change, compare properties (excluding internal fields as defined in hash)
                    old_props = self.get_attribute_values(old_feature, exclude_fields)

                    # For comparision prepare properties and geometry 
                    new_props = self.get_attribute_values(new_feature, exclude_fields)
                    
                    # Find what changed
                    for key in set(old_props.keys()) | set(new_props.keys()):
                        if old_props.get(key) != new_props.get(key):

                            # Changes after download time by other users labeled as red area. Use last change done by other
                            if red_changes.get(row_guid) and red_changes.get(row_guid)['change_type'] == "delete":
                                conflict_details['properties'][key] = {
                                    'current_value': new_props.get(key),
                                    'conflict_value': "-",
                                    'conflict_type': red_changes.get(row_guid)['change_type'],
                                    'conflict_time': red_changes.get(row_guid)['timestamp'],
                                    'conflict_user': red_changes.get(row_guid)['userid']
                                }
                            elif red_changes.get(row_guid) and red_changes.get(row_guid)['properties'][key]:
                                conflict_details['properties'][key] = {
                                    'current_value': new_props.get(key),
                                    'conflict_value': red_changes.get(row_guid)['properties'][key]['new_value'],
                                    'conflict_type': red_changes.get(row_guid)['change_type'],
                                    'conflict_time': red_changes.get(row_guid)['timestamp'],
                                    'conflict_user': red_changes.get(row_guid)['userid']
                                }
                            else:
                                change_details['properties'][key] = {
                                    'old_value': old_props.get(key),
                                    'new_value': new_props.get(key)
                                }
                
                # If geometries are different
                if (new_geometry_hash != old_geometry_hash):

                    if (old_feature['geometry']['type'] != new_feature['geometry']['type']):

                        # Changes after download time by other users labeled as red area. Use last change done by others
                        if red_changes.get(row_guid) and red_changes.get(row_guid)['change_type'] == "delete":
                            conflict_details['geometry']['type'] = {
                                'current_value': new_feature['geometry']['type'],
                                'conflict_value': "-",
                                'conflict_type': red_changes.get(row_guid)['change_type'],
                                'conflict_time': red_changes.get(row_guid)['timestamp'],
                                'conflict_user': red_changes.get(row_guid)['userid']
                            }
                        elif red_changes.get(row_guid) and red_changes.get(row_guid)['geometry']:
                            conflict_details['geometry']['type'] = {
                                'current_value': new_feature['geometry']['type'],
                                'conflict_value': red_changes.get(row_guid)['geometry']['type']['new_value'],
                                'conflict_type': red_changes.get(row_guid)['change_type'],
                                'conflict_time': red_changes.get(row_guid)['timestamp'],
                                'conflict_user': red_changes.get(row_guid)['userid']
                            }
                        else:
                            change_details['geometry']['type'] = {
                                'new_value': new_feature['geometry']['type']
                            }
                    if (old_feature['geometry']['coordinates'] != new_feature['geometry']['coordinates']):

                        # Changes after download time by other users labeled as red area. Use last change done by others
                        if red_changes.get(row_guid) and red_changes.get(row_guid)['geometry']:
                            conflict_details['geometry']['coordinates'] = {
                                'current_value': 'geometry1',
                                'conflict_value': 'geometry2',
                                'conflict_type': red_changes.get(row_guid)['change_type'],
                                'conflict_time': red_changes.get(row_guid)['timestamp'],
                                'conflict_user': red_changes.get(row_guid)['userid']
                            }
                        else:
                            change_details['geometry']['coordinates'] = {
                                'new_value': new_feature['geometry']['coordinates']
                            }
                if len(change_details['properties']) != 0 or len(change_details['geometry']) != 0:     
                    result['changed_features'].append(change_details)
                if len(conflict_details['properties']) != 0 or len(conflict_details['geometry']) != 0:    
                    result['conflicts'].append(conflict_details)
            
            # New feature added
            else:

                # If feature is not deleted by another user then add as an insert
                if row_guid not in red_changes:

                    # This feature has been inserted
                    change_details = {
                        'row_guid': row_guid,
                        'change_type': 'insert',
                        'geometry': {},
                        'properties': {},
                    }

                    # For comparision prepare properties and geometry 
                    new_props = self.get_attribute_values(new_feature, exclude_fields)
                    
                    # Add feature with attributes and geometries
                    for key in new_props.keys():
                        change_details['properties'][key] = {
                            'new_value': new_props.get(key)
                        }
                    change_details['geometry']['type'] = {
                        'new_value': new_feature['geometry']['type']
                    }
                    change_details['geometry']['coordinates'] = {
                        'new_value': new_feature['geometry']['coordinates']
                    }
                        
                    result['changed_features'].append(change_details)
        
        # Check for deleted features
        for row_guid, old_feature in old_features_map.items():
            if row_guid not in new_features_map:

                # If feature is not updated by another user then delete from dict
                if row_guid not in red_changes:
                    change_details = {
                        'row_guid': row_guid,
                        'change_type': 'delete'
                    }
                    result['changed_features'].append(change_details)
                else:
                    # This feature has changes
                    conflict_details = {
                        'row_guid': row_guid,
                        'change_type': 'delete',
                        'geometry': {},
                        'properties': {}
                    }
                    conflict_details['geometry']['type'] = {
                        'current_value': 'deleted',
                        'conflict_value': old_feature['geometry']['type'],
                        'conflict_type': red_changes.get(row_guid)['change_type'],
                        'conflict_time': red_changes.get(row_guid)['timestamp'],
                        'conflict_user': red_changes.get(row_guid)['userid']
                    }
                    result['conflicts'].append(conflict_details)
         
        return result