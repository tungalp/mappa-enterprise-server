from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.spatial.file_store.file_store_model import CreateFileStore, UpdateAllFileStore, UpdateFileStore, FileStore
from mapa.spatial.file_store.file_store_repository import FileStoreRepository

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import copy


class FileStoreService(BaseEntityService[FileStoreRepository, FileStore, CreateFileStore, UpdateFileStore, UpdateAllFileStore]):
    """FileStore Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, FileStoreRepository, FileStore)



# data_diff json file example Bekir 06.09.2025
""" change_actions: {
  "2023-10-20T09:15:30": {
    "userid": "user_456",
    "changed_features": [
      {
        "coord_key": 67890,
        "change_type": "insert",
        "attributes": [{"public_space":{old_value:"kgjf", new_value:"fghg"},
                              {"area_sqkm":{old_value:"kgjf", new_value:"fghg"}
        }],

      },
      {
        "coord_key": 67891,
        "name": "North Garden",
        "type": "community_garden",
        "plot_count": 24
      }
    ]
  },
  "2023-10-22T16:45:12": {
    "userid": "user_789",
    "diffs": {
      "id": 12345,
      "status": "active"
    }
  },
  }
"""


class GeoJSONConflictResolver:
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

    def add_download_time(geojson_data):
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
        
        return None
    
    def find_feature_by_id(self, geojson_data: Dict[str, Any], object_id: Any) -> Optional[Dict[str, Any]]:
        """Find a feature by its object ID"""
        for feature in geojson_data['features']:
            if feature.get('id') == object_id:
                return feature
        return None

    def exclude_fields() -> Optional[List[str]]:
        return [
            'last_updated', 'download_time', 'processing_timestamp', 
            'row_id', 'created_at', 'modified_at', 'updated_at',
            'timestamp', 'sync_time', 'import_date'
        ]

    def normalize_coordinates(self, coords, precision: int = 6):
        """Normalize coordinate precision for consistent comparison"""
        if isinstance(coords, list):
            if isinstance(coords[0], (int, float)):
                # Single coordinate pair [lon, lat] or [lon, lat, elevation]
                return tuple(round(c, precision) for c in coords)
            else:
                # Nested coordinates
                return tuple(self.normalize_coordinates(self, c, precision) for c in coords)
        return coords

    def get_coordinate_key(self, feature: Dict[str, Any], precision: int = 6) -> str:
        """
        Generate a coordinate-based key for feature identification
        
        Args:
            feature: GeoJSON feature
            precision: Decimal precision for coordinate rounding
            
        Returns:
            String key based on normalized coordinates
        """
        geometry = feature.get('geometry', {})
        coords = geometry.get('coordinates')
        
        if not coords:
            return None
            
        # Normalize coordinates
        normalized_coords = self.normalize_coordinates(coords, precision)
        
        # Create key from geometry type + coordinates
        geom_type = geometry.get('type', '')
        coord_str = json.dumps(normalized_coords, separators=(',', ':'))
        
        return f"{geom_type}:{coord_str}"

    def get_feature_hash(self, feature: Dict[str, Any], 
                        exclude_fields: List[str] = None) -> str:
        """
        Generate SHA256 hash for GeoJSON feature based on id, type, geometry, and properties
        
        Args:
            feature: GeoJSON feature dictionary
            coordinate_precision: Number of decimal places for coordinate rounding
            exclude_fields: List of property fields to exclude from hash
            
        Returns:
            SHA256 hash string
        """
        
        # Build normalized feature for hashing
        normalized = {}
        
        # Include type
        if 'type' in feature:
            normalized['type'] = feature['type']
        
        # Include id
        if 'id' in feature:
            normalized['id'] = feature['id']
        
        # Include filtered properties
        if 'properties' in feature:
            normalized['properties'] = {
                k: v for k, v in feature['properties'].items() 
                if k not in exclude_fields
            }
        
        # Convert to JSON string with consistent ordering
        feature_str = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA256 hash
        return hashlib.sha256(feature_str.encode('utf-8')).hexdigest()

    def compare_change_geojson_features(self, reconstructed_features: Dict[str, Any], 
                               new_features: Dict[str, Any], reconstructed_changes:List[str]) -> Dict[str, Any]:
        """
        Compare two GeoJSON files and identify changes
        
        Returns:
            Dict with:
            - unchanged_features: Features that haven't changed
            - changed_features: Features that have changed with change details
        """
        result = {
            'unchanged_features': [],
            'changed_features': [],
            'conflicts': []
        }
        
        # Create maps using coordinate keys
        exclude_fields = self.exclude_fields()
        old_features_map = {}
        for f in reconstructed_features:
            coord_key = self.get_coordinate_key(f)
            if coord_key:  # Skip features without valid coordinates
                coord_key = hashlib.sha256(coord_key.encode('utf-8')).hexdigest()
                content_hash = self.get_feature_hash(f, exclude_fields)
                f['content_hash'] = content_hash
                old_features_map[coord_key] = f
        
        new_features_map = {}
        for f in new_features:
            coord_key = self.get_coordinate_key(f)
            if coord_key:  # Skip features without valid coordinates
                coord_key = hashlib.sha256(coord_key.encode('utf-8')).hexdigest()
                content_hash = self.get_feature_hash(f, exclude_fields)
                f['content_hash'] = content_hash
                new_features_map[coord_key] = f
        
        # Check all features in the new GeoJSON
        for coord_key, new_feature in new_features_map.items():
            if coord_key in old_features_map:

                # Feature exists at same coordinates
                old_feature = old_features_map[coord_key]

                # Check all properties are same or not with hash
                new_feature_hash = new_feature['content_hash']
                old_feature_hash = old_feature['content_hash']
                if new_feature_hash == old_feature_hash:
                    result['unchanged_features'].append(coord_key)
                    continue

                # There is change, compare properties (excluding internal fields as defined in hash)
                old_props = {k: v for k, v in (old_feature['properties'].items() + old_feature['type'] + old_feature['id'])}

                # For comparision prepare properties and geometry 
                new_props = {k: v for k, v in (new_feature['properties'].items() + new_feature['type'] + new_feature['id'])}

                # This feature has changes
                change_details = {
                    'coord_key': coord_key,
                    'change_type': 'update',
                    'attributes': {}
                }
                
                # Find what changed
                for key in set(old_props.keys()) | set(new_props.keys()):
                    if old_props.get(key) != new_props.get(key):
                        change_details['attributes'][key] = {
                            'old_value': old_props.get(key),
                            'new_value': new_props.get(key)
                        }
                        if reconstructed_changes.get(coord_key):
                            new_features[key] = reconstructed_changes.get(coord_key)["last_changes"][key]['new_value']

                result['changed_features'].append(change_details)
               
            else:
                # New feature added
                change_details = {
                    'coord_key': coord_key,
                    'change_type': 'insert',
                    'attributes': {}
                }

                # For comparision prepare properties and geometry 
                new_props = {k: v for k, v in (new_feature['properties'].items() + new_feature['type'] + new_feature['id'])
                            if k not in exclude_fields}
                
                # Find what inserted
                for key in new_props.keys():
                    change_details['attributes'][key] = {
                        'new_value': new_props.get(key)
                    }
                result['changed_features'].append(change_details)
        
        # Check for deleted features
        for coord_key, old_feature in old_features_map.items():
            if coord_key not in new_features_map:
                change_details = {
                    'coord_key': coord_key,
                    'change_type': 'delete',
                    'attributes': {}
                }

                # For comparision prepare properties and geometry 
                old_props = {k: v for k, v in (old_feature['properties'].items() + old_feature['type'] + old_feature['id'])
                            if k not in exclude_fields}
                
                # Find what deleted
                for key in old_feature.keys():
                    change_details['attributes'][key] = {
                        'old_value': new_props.get(key)
                    }

                # If deleted feature is changed by another user re-add
                if coord_key not in reconstructed_changes:
                    new_features.append(old_feature)

                result['changed_features'].append(change_details)
        
        return result, new_features
    
    def reconstruct_original_features(self, db_geojson: Dict[str, Any], target_time: datetime) -> List[str]:
        """
        Reconstruct original GeoJSON data at a specific point in time by reversing changes
        
        Args:
            db_geojson: Current GeoJSON with change history in 'changed_features' key
            target_time: Target datetime to reconstruct data for
            
        Returns:
            Reconstructed GeoJSON as it existed at target_time
        """
        
        # Get current features (assuming they exist in 'features' key)
        current_features = {}
        if 'features' in db_geojson:
            for feature in db_geojson['features']:
                coord_key = self.get_coordinate_key(feature)
                if coord_key:
                    coord_key = hashlib.sha256(coord_key.encode('utf-8')).hexdigest()
                    current_features[coord_key] = feature
        
        # Process change history to reconstruct original state
        changed_actions = db_geojson.get('changed_actions', {})
        
        # Collect all changes after target_time, grouped by coord_key and attribute
        changes_to_reverse = {}
        
        for timestamp_str, change_group in changed_actions.items():
            try:
                # Parse timestamp (assuming ISO format like "2023-10-20T09:15:30")
                change_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                
                # Only process changes that happened AFTER our target time
                if change_time <= target_time:
                    continue
                    
                userid = change_group.get('userid')
                changed_features = change_group.get('changed_features', [])
                
                # Process each diff in this timestamp
                for change in changed_features:
                    coord_key = change.get('coord_key')
                    change_type = change.get('change_type')  # 'update', 'insert', 'delete'
                    attributes = change.get('attributes', {})
                    
                    if not coord_key:
                        continue
                    
                    # Initialize tracking for this coordinate
                    if coord_key not in changes_to_reverse:
                        changes_to_reverse[coord_key] = {
                            'first_changes': {},  # First change for each attribute after target_time
                            'change_type': change_type,
                            'timestamp': change_time
                        }
                    
                    # For each changed attribute, keep only the FIRST change after target_time
                    for attr_name, change_detail in attributes.items():
                        if attr_name not in changes_to_reverse[coord_key]['first_changes']:
                            # This is the first change we've seen for this attribute after target_time
                            changes_to_reverse[coord_key]['first_changes'][attr_name] = {
                                'old_value': change_detail.get('old_value'),
                                'new_value': change_detail.get('new_value'),
                                'timestamp': change_time,
                                'change_type': change_type,
                                'userid': userid
                            }
                            changes_to_reverse[coord_key]['last_changes'][attr_name]
                        else:   
                            # Update the change type if this is earlier than what we had
                            change_time_in_reverse = changes_to_reverse[coord_key]['first_changes'][attr_name]["timestamp"]
                            if change_time < change_time_in_reverse:
                                # Change if this value is earlier then value that is added to changes_to_reverse before
                                changes_to_reverse[coord_key]['first_changes'][attr_name] = {
                                    'old_value': change_detail.get('old_value'),
                                    'new_value': change_detail.get('new_value'),
                                    'timestamp': change_time,
                                    'change_type': change_type,
                                    'userid': userid
                                }
                            else:
                                # Change if this value is earlier then value that is added to changes_to_reverse before
                                changes_to_reverse[coord_key]['last_changes'][attr_name] = {
                                    'old_value': change_detail.get('old_value'),
                                    'new_value': change_detail.get('new_value'),
                                    'timestamp': change_time,
                                    'change_type': change_type,
                                    'userid': userid
                                }
                # Update the overall change type if this is earlier than what we had
                if change_time < changes_to_reverse[coord_key]['timestamp']:
                    changes_to_reverse[coord_key]['change_type'] = change_type
                    changes_to_reverse[coord_key]['timestamp'] = change_time

            except (ValueError, AttributeError) as e:
                # Skip invalid timestamps
                continue
        
        # Now apply the changes in reverse to reconstruct original state
        features_to_reconstruct = []
        
        for coord_key, change_info in changes_to_reverse.items():
            change_type = change_info['change_type']
            first_changes = change_info['first_changes']
            
            if change_type == 'insert':
                # Feature was inserted after target_time, so it shouldn't exist in reconstructed data
                # Remove it if it exists in current features
                if coord_key in current_features:
                    # Don't include this feature in reconstructed data
                    pass
                    
            elif change_type == 'delete':
                # Feature was deleted after target_time, so it should exist in reconstructed data
                # Try to reconstruct it from the old_values in the delete change
                reconstructed_feature = {
                    'type': 'Feature',
                    'geometry': {},
                    'properties': {}
                }
                
                # Reconstruct from old_values
                for attr_name, change_detail in first_changes.items():
                    old_value = change_detail['old_value']
                    
                    if attr_name == 'type':
                        reconstructed_feature['type'] = old_value
                    elif attr_name == 'id':
                        reconstructed_feature['id'] = old_value
                    elif attr_name.startswith('geometry'):
                        # Handle geometry attributes
                        if attr_name == 'geometry':
                            reconstructed_feature['geometry'] = old_value
                        else:
                            # Handle nested geometry properties
                            reconstructed_feature['geometry'][attr_name.replace('geometry.', '')] = old_value
                    else:
                        # Regular property
                        reconstructed_feature['properties'][attr_name] = old_value
                
                features_to_reconstruct.append(reconstructed_feature)
                
            elif change_type == 'update':
                # Feature was updated after target_time, restore old values
                if coord_key in current_features:
                    feature = copy.deepcopy(current_features[coord_key])
                    
                    # Apply old values to restore original state
                    for attr_name, change_detail in first_changes.items():
                        old_value = change_detail['old_value']
                        
                        if attr_name == 'type':
                            feature['type'] = old_value
                        elif attr_name == 'id':
                            feature['id'] = old_value
                        elif attr_name.startswith('geometry'):
                            # Handle geometry attributes
                            if attr_name == 'geometry':
                                feature['geometry'] = old_value
                            else:
                                # Handle nested geometry properties
                                geom_attr = attr_name.replace('geometry.', '')
                                if 'geometry' not in feature:
                                    feature['geometry'] = {}
                                feature['geometry'][geom_attr] = old_value
                        else:
                            # Regular property
                            if 'properties' not in feature:
                                feature['properties'] = {}
                            feature['properties'][attr_name] = old_value
                    
                    features_to_reconstruct.append(feature)
        
        # Include unchanged features (features that weren't modified after target_time)
        for coord_key, feature in current_features.items():
            if coord_key not in changes_to_reverse:
                features_to_reconstruct.append(copy.deepcopy(feature))
        
        return features_to_reconstruct, changes_to_reverse
    
    
    def apply_changes(self, db_geojson: Dict[str, Any], user_geojson: Dict[str, Any], userid: str) -> Dict[str, Any]:
        """
        Apply user changes to the database GeoJSON with conflict resolution
        """
        # Extract download_time from user's GeoJSON
        download_time = self.extract_download_time(user_geojson)
        if not download_time:
            return {
                'success': False,
                'error': 'download_time not found in user GeoJSON',
                'conflicts': [],
                'applied_changes': []
            }
        
        # Reconstruct original data as it was at download_time
        reconstructed_features, reconstructed_changes = self.reconstruct_original_features(db_geojson, download_time)
        new_features = user_geojson.get('features', [])

        # Compare user's changes with original data
        comparison, updated_features = self.compare_change_geojson_features(reconstructed_features, new_features, reconstructed_changes)
        
        # Check for conflicts in changed features
        for change in comparison['changed_features']:
            com_coord_key = change['coord_key']
            com_change_type = change.get('change_type')  # 'update', 'insert', 'delete'
            com_attributes = change.get('attributes', {})    
                    
            # Check if any of the user's changes conflict with subsequent changes
            conflicting_attributes = []
            user_changes = []

            # Check if this attribute was changed by others
            if com_coord_key in reconstructed_changes:
                sub_change = reconstructed_changes.get(com_coord_key)
                sub_last_changes = sub_change.get("last_changes")
                
                # The user is trying to change an attribute that was already changed by others
                for sub_attribute_name, sub_attribute_changes in sub_last_changes:
                    if sub_attribute_name in com_attributes:
                        com_attribute_changes = com_attributes.get(sub_attribute_name)

                        conflicting_attributes.append({
                            'attribute': sub_attribute_name,
                            'changed_from': sub_attribute_changes.get('old_value'),
                            'changed_to': sub_attribute_changes.get('new_value'),
                            'change_type': sub_attribute_changes['change_type'],
                            'user': sub_attribute_changes['userid'],
                            'changed_at': sub_attribute_changes['timestamp'],
                        })
                        user_changes.append({
                            'attribute': sub_attribute_name,
                            'changed_from': com_attribute_changes.get('old_value'),
                            'changed_to': com_attribute_changes.get('new_value'),
                            'change_type': com_change_type,
                            'user': userid,
                        })

                        # Use last changes for conflict
                        if com_change_type == "update":
                            com_attribute_changes.set('new_value', sub_attribute_changes.get('new_value'))
                        if com_change_type == "delete":
                            comparison['changed_features'].remove(change)

                if conflicting_attributes:
                    # There are conflicts - this object was changed by others
                    conflict_details = {
                        'coord_key': com_coord_key,
                        'user_changes': user_changes,
                        'conflicting_attributes': conflicting_attributes
                    }
                    comparison['conflicts'].append(conflict_details)
                
        return comparison, updated_features 
    
""" # Example usage
if __name__ == "__main__":
    # Initialize the conflict resolver
    resolver = GeoJSONConflictResolver()
    
    # Load GeoJSON files
    db_geojson = resolver.load_geojson('database_data.geojson')
    user_geojson = resolver.load_geojson('user_changes.geojson')
    
    # User ID making the changes
    user_id = "user123"
    
    # Apply changes with conflict detection
    comparison, updated_features  = resolver.apply_changes(db_geojson, user_geojson, user_id)
    
    # Update changed_features in new geojson file from comparison json
    # Update features in new geojson file from comparison json """


