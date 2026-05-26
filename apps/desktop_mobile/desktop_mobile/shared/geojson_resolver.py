import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
import hashlib
import copy
import uuid
import base64
from desktop_mobile.shared.utils import convert_download_time
from anyio import open_file
from fastapi.concurrency import run_in_threadpool

class GeoJSONConflictResolver:
    row_guid = "row_guid"
    
    exclude_fields = [
        'fid', 'last_updated', 'download_time', 'processing_timestamp', 
        'row_id', 'created_at', 'modified_at', 'updated_at',
        'timestamp', 'sync_time', 'import_date'
    ]
    
    def __init__(self):
        self.change_history = []

    async def load_geojson_store_async(self, file_store):
        await file_store.seek(0)
        file_geojson = await run_in_threadpool(json.load, file_store.file)
        return file_geojson
    
    def load_geojson(self, file_path: str) -> Dict[str, Any]:
        """Load GeoJSON from file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def load_geojson_path_async(self, file_path: str):
        """
        Reads a GeoJSON file from a disk path asynchronously.
        """
        def _load_geojson():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        try:
            geojson_data = await run_in_threadpool(_load_geojson)
            return geojson_data
        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON. {e}")
            return None
    
    def save_geojson(self, data: Dict[str, Any], file_path: str):
        """Save GeoJSON to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    async def save_geojson_async(self, geojson_dict, file_path):
        content = json.dumps(geojson_dict, indent=4, ensure_ascii=False)
        async with await open_file(file_path, mode="w", encoding="utf-8") as f:
            await f.write(content)

    def add_update_download_time(self, geojson_data):
        """
        Add download_time to GeoJSON when user downloads data
        """
        current_time = datetime.now(timezone.utc).isoformat()
        if 'metadata' not in geojson_data:
            geojson_data['metadata'] = {}
        geojson_data['metadata']['download_time'] = current_time
        return geojson_data

    def add_guid_to_geojson(self, geojson: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Adds id to GeoJSON features if it doesn't exist.        
        """
        if isinstance(geojson, str):
            try:
                geojson = json.loads(geojson)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")
        
        if not isinstance(geojson, dict):
            raise TypeError("Input must be a dictionary or valid JSON string")
        
        if 'type' not in geojson:
            raise ValueError('Invalid GeoJSON: missing "type" property')
        
        result = geojson.copy()
        if result['type'] == 'FeatureCollection':
            if 'features' not in result or not isinstance(result['features'], list):
                raise ValueError('Invalid GeoJSON FeatureCollection: missing or invalid "features" array')
            result['features'] = [self.add_guid_to_feature(feature) for feature in result['features']]
        elif result['type'] == 'Feature':
            result = self.add_guid_to_feature(result)
        return result
    
    def add_guid_to_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single GeoJSON feature, adding id if needed.
        """       
        if not isinstance(feature, dict):
            raise ValueError("Feature must be a dictionary")
        processed_feature = feature.copy()
        if self.row_guid not in processed_feature:
            processed_feature[self.row_guid] = str(uuid.uuid4())
        return processed_feature

    def base64_to_geojson(self, base64_data: str) -> Dict[str, Any]:
        try:
            decoded_bytes = base64.b64decode(base64_data)
            json_string = decoded_bytes.decode('utf-8')
            geojson_data = json.loads(json_string)
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
        try:
            if not isinstance(geojson_data, dict):
                raise ValueError("Input data is not a valid dictionary object")
            if 'type' not in geojson_data:
                raise ValueError("Missing 'type' field - not a valid GeoJSON")
            json_string = json.dumps(geojson_data, separators=(',', ':'))
            json_bytes = json_string.encode('utf-8')
            base64_data = base64.b64encode(json_bytes)
            return base64_data
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot serialize GeoJSON to JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error encoding to base64: {e}")

    def blob_to_geojson(self, blob_data: bytes):
        try:
            json_str = blob_data.decode("utf-8-sig").strip()
            geojson_dict = json.loads(json_str)
            if "type" not in geojson_dict:
                raise ValueError("Data is valid JSON but not a valid GeoJSON object.")
            return geojson_dict
        except UnicodeDecodeError as e:
            raise ValueError("The file encoding is not UTF-8.")
        except json.JSONDecodeError as e:
            raise ValueError(f"The file is not a valid JSON. Error: {e.msg} at line {e.lineno} column {e.colno}")
        
    def geojson_to_blob(self, geojson_dict: dict, minify: bool = True):
        try:
            if minify:
                json_str = json.dumps(geojson_dict, separators=(',', ':'))
            else:
                json_str = json.dumps(geojson_dict, indent=4)
            blob_data = json_str.encode("utf-8")
            return blob_data
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error converting dictionary to JSON: {e}")
        
    def validate_geojson(self, geojson: Dict[str, Any]) -> bool:
        if not isinstance(geojson, dict):
            return False
        geojson_type = geojson.get('type')
        valid_types = ['FeatureCollection', 'Feature', 'Point', 'LineString', 
                    'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon', 
                    'GeometryCollection']
        if geojson_type not in valid_types:
            return False
        if geojson_type == 'FeatureCollection':
            if 'features' not in geojson or not isinstance(geojson['features'], list):
                return False
        elif geojson_type == 'Feature':
            required_keys = ['properties', 'geometry']
            if not all(key in geojson for key in required_keys):
                return False
        return True

    def validate_geojson_structure(self, geojson: Dict[str, Any]) -> bool:
        try:
            if geojson.get('type') == 'FeatureCollection':
                if 'features' not in geojson or not isinstance(geojson['features'], list):
                    return False
                for feature in geojson['features']:
                    if not self._is_valid_feature(feature):
                        return False
            elif geojson.get('type') == 'Feature':
                return self._is_valid_feature(geojson)
            return True
        except Exception:
            return False

    def _is_valid_feature(self, feature: Dict[str, Any]) -> bool:
        if not isinstance(feature, dict):
            return False
        required_keys = ['type', 'properties', 'geometry']
        if not all(key in feature for key in required_keys):
            return False
        if feature['type'] != 'Feature':
            return False
        if feature['properties'] is not None and not isinstance(feature['properties'], dict):
            return False
        if feature['geometry'] is not None and not isinstance(feature['geometry'], dict):
            return False
        return True

    def extract_download_time(self, geojson_data: Dict[str, Any]) -> Optional[datetime]:
        if 'metadata' in geojson_data and 'download_time' in geojson_data['metadata']:
            return convert_download_time(geojson_data['metadata']['download_time'])
        if 'features' in geojson_data and len(geojson_data['features']) > 0:
            first_feature = geojson_data['features'][0]
            if 'properties' in first_feature and 'download_time' in first_feature['properties']:
                return convert_download_time(first_feature['properties']['download_time'])
        return datetime.now(timezone.utc)
        
    def find_feature_by_id(self, geojson_data: Dict[str, Any], object_id: Any) -> Optional[Dict[str, Any]]:
        for feature in geojson_data['features']:
            if feature.get(self.row_guid) == object_id:
                return feature
        return None

    def normalize_coordinates(self, coords, precision: int = 6):
        if isinstance(coords, list):
            if isinstance(coords[0], (int, float)):
                return tuple(float(round(c, precision)) for c in coords)
            else:
                return tuple(self.normalize_coordinates(c) for c in coords)
        return coords

    def get_geometry_hash(self, feature: Dict[str, Any]) -> str:
        geometry = feature.get('geometry')
        if not geometry:
            return "no_geometry"

        coords = geometry.get('coordinates')
        geom_type = geometry.get('type', '')

        if coords is None:
            return "empty_coords"

        normalized_coords = self.normalize_coordinates(coords)
        coord_str = json.dumps(normalized_coords, separators=(',', ':'), sort_keys=True)
        coord_key = f"{geom_type}:{coord_str}"
        return hashlib.sha256(coord_key.encode('utf-8')).hexdigest()    
    
    def get_attribute_values(self, feature: Dict[str, Any], 
                           exclude_fields: List[str] = None) -> Optional[Dict[str, Any]]:
        if exclude_fields is None:
            exclude_fields = []
        attribute_values = {}
        if 'properties' in feature and isinstance(feature['properties'], dict):
            for attribute in feature['properties']:
                if attribute not in exclude_fields:
                    attribute_values[attribute] = feature['properties'][attribute]
        return attribute_values 

    def get_properties_hash(self, feature: Dict[str, Any], 
                           exclude_fields: List[str] = None) -> str:
        if exclude_fields is None:
            exclude_fields = []
        attribute_values = self.get_attribute_values(feature, exclude_fields)
        feature_str = json.dumps(attribute_values, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(feature_str.encode('utf-8')).hexdigest()

    def add_changed_features(self, db_geojson: Dict[str, Any], comparison: Dict[str, Any], userid: str) -> Dict[str, Any]:
        if 'changes' not in db_geojson:
            db_geojson['changes'] = {}
        current_timestamp = datetime.now(timezone.utc).isoformat()
        if current_timestamp not in db_geojson['changes']:
            db_geojson['changes'][current_timestamp] = {}  
        db_geojson['changes'][current_timestamp]['userid'] = userid
        db_geojson['changes'][current_timestamp]['changed_features'] = comparison['changed_features']
        return db_geojson

    def sort_by_date_keys(self, data_dict, reverse=False):
        return sorted(data_dict.items(), 
                    key=lambda x: convert_download_time(x[0]), 
                    reverse=reverse)

    def reconstruct_to_time(self, db_geojson: Dict[str, Any], download_time: datetime) -> List[str]:
        if download_time is None:
            download_time = datetime.now(timezone.utc)
        changed_actions = db_geojson.get('changes', {})
        green_changes = {}
        red_changes = {}
        downloaded_features = []
        if "features" in db_geojson:
            downloaded_features = copy.deepcopy(db_geojson["features"])
        
        for timestamp_str, change_group in self.sort_by_date_keys(changed_actions):
            try:
                upload_time = convert_download_time(timestamp_str)
                userid = change_group.get('userid')
                changed_features = change_group.get('changed_features', [])
                
                for change in changed_features:
                    row_guid = change.get(self.row_guid)
                    change_type = change.get('change_type')
                    geometry = change.get('geometry', {})
                    properties = change.get('properties', {})

                    if upload_time > download_time:
                        if row_guid not in red_changes:
                            red_changes[row_guid] = {
                                'change_type': change_type,
                                'geometry': {},
                                'properties': {},
                                'timestamp': upload_time,
                                'userid': userid
                            }
                        for attr_name, change_detail in geometry.items():
                            red_changes[row_guid]['geometry'][attr_name] = {
                                'new_value': change_detail.get('new_value'),
                                'change_type': change_type,
                                'timestamp': upload_time,
                                'userid': userid
                            }
                        for attr_name, change_detail in properties.items():
                            red_changes[row_guid]['properties'][attr_name] = {
                                'new_value': change_detail.get('new_value'),
                                'change_type': change_type,
                                'timestamp': upload_time,
                                'userid': userid
                            }
                    else:
                        green_changes[row_guid] = {
                            'change_type': change_type,
                            'geometry': {},
                            'properties': {}
                        }
                        for attr_name, change_detail in geometry.items():
                            green_changes[row_guid]['geometry'][attr_name] = {
                                'new_value': change_detail.get('new_value'),
                                'change_type': change_type
                            }
                        for attr_name, change_detail in properties.items():
                            green_changes[row_guid]['properties'][attr_name] = {
                                'new_value': change_detail.get('new_value'),
                                'change_type': change_type,
                            }
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
                            downloaded_features.append(reconstructed_feature)
                        elif change_type == 'update':
                            for i, feature in enumerate(downloaded_features):
                                if feature.get('row_guid') == row_guid:
                                    for key, value in geometry.items():
                                        feature['geometry'][key] = value['new_value']
                                    for key, value in properties.items():
                                        feature['properties'][key] = value['new_value']
                        elif change_type == 'delete':
                            for i, feature in enumerate(downloaded_features):
                                if feature.get('row_guid') == row_guid:
                                    del downloaded_features[i]
                                    break
            except Exception as e:
                print(f"Error reconstructing frame: {e}")
                continue

        return downloaded_features, red_changes
    
    def find_changes_with_conflicts(self, downloaded_features: Dict[str, Any], 
                               new_features: Dict[str, Any], red_changes: List[str]) -> Dict[str, Any]:
        result = {
            'unchanged_features': [],
            'changed_features': [],
            'conflicts': []
        }
        
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
        
        for row_guid, new_feature in new_features_map.items():
            if row_guid in old_features_map:
                old_feature = old_features_map[row_guid]
                new_properties_hash = new_feature['properties_hash']
                old_properties_hash = old_feature['properties_hash']
                new_geometry_hash = new_feature['geometry_hash']
                old_geometry_hash = old_feature['geometry_hash']

                change_details = {
                    'row_guid': row_guid,
                    'change_type': 'update',
                    'geometry': {},
                    'properties': {},
                }
                conflict_details = {
                    'row_guid': row_guid,
                    'change_type': 'update',
                    'geometry': {},
                    'properties': {},
                }

                if (new_properties_hash == old_properties_hash and new_geometry_hash == old_geometry_hash):
                    result['unchanged_features'].append(row_guid)
                    continue

                if (new_properties_hash != old_properties_hash):
                    old_props = self.get_attribute_values(old_feature, exclude_fields)
                    new_props = self.get_attribute_values(new_feature, exclude_fields)
                    
                    for key in set(old_props.keys()) | set(new_props.keys()):
                        if old_props.get(key) != new_props.get(key):
                            if red_changes.get(row_guid) and red_changes.get(row_guid)['change_type'] == "delete":
                                conflict_details['properties'][key] = {
                                    'current_value': new_props.get(key),
                                    'conflict_value': "-",
                                    'conflict_type': red_changes.get(row_guid)['change_type'],
                                    'conflict_time': red_changes.get(row_guid)['timestamp'],
                                    'conflict_user': red_changes.get(row_guid)['userid']
                                }
                            elif red_changes.get(row_guid) and red_changes.get(row_guid)['properties'].get(key):
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
                
                if (new_geometry_hash != old_geometry_hash):
                    if (old_feature['geometry']['type'] != new_feature['geometry']['type']):
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
            else:
                if row_guid not in red_changes:
                    change_details = {
                        'row_guid': row_guid,
                        'change_type': 'insert',
                        'geometry': {},
                        'properties': {},
                    }
                    new_props = self.get_attribute_values(new_feature, exclude_fields)
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
        
        for row_guid, old_feature in old_features_map.items():
            if row_guid not in new_features_map:
                if row_guid not in red_changes:
                    change_details = {
                        'row_guid': row_guid,
                        'change_type': 'delete'
                    }
                    result['changed_features'].append(change_details)
                else:
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

    def resolve_recursive_changes(self, 
                                previous_result: Dict[str, Any], 
                                red_changes: Dict[str, Any]) -> Dict[str, Any]:
        final_result = {
            'unchanged_features': previous_result.get('unchanged_features', []),
            'changed_features': [],
            'conflicts': previous_result.get('conflicts', []) 
        }

        for change in previous_result.get('changed_features', []):
            row_guid = change['row_guid']
            
            if row_guid not in red_changes:
                final_result['changed_features'].append(change)
                continue

            red_change = red_changes[row_guid]
            conflict_details = {
                'row_guid': row_guid,
                'change_type': change.get('change_type'),
                'geometry': {},
                'properties': {}
            }

            if red_change.get('change_type') == "delete":
                conflict_details['geometry']['type'] = {
                    'current_value': change.get('geometry', {}).get('type', {}).get('new_value', 'unknown'),
                    'conflict_value': "-",
                    'conflict_type': "delete",
                    'conflict_time': red_change.get('timestamp'),
                    'conflict_user': red_change.get('userid')
                }
                final_result['conflicts'].append(conflict_details)
                continue 

            change_props = change.get('properties', {})
            red_props = red_change.get('properties', {})
            
            for key in list(change_props.keys()):
                if key in red_props:
                    conflict_details['properties'][key] = {
                        'current_value': change_props[key].get('new_value'),
                        'conflict_value': red_props[key].get('new_value'),
                        'conflict_type': red_change.get('change_type'),
                        'conflict_time': red_change.get('timestamp'),
                        'conflict_user': red_change.get('userid')
                    }
                    del change['properties'][key]

            if change.get('geometry') and red_change.get('geometry'):
                for geo_key in ['type', 'coordinates']:
                    if geo_key in change['geometry'] and geo_key in red_change['geometry']:
                        conflict_details['geometry'][geo_key] = {
                            'current_value': change['geometry'][geo_key].get('new_value'),
                            'conflict_value': red_change['geometry'][geo_key].get('new_value'),
                            'conflict_type': red_change.get('change_type'),
                            'conflict_time': red_change.get('timestamp'),
                            'conflict_user': red_change.get('userid')
                        }
                change['geometry'] = {}

            if conflict_details['properties'] or conflict_details['geometry']:
                final_result['conflicts'].append(conflict_details)
            
            if change.get('properties') or change.get('geometry'):
                final_result['changed_features'].append(change)

        return final_result
