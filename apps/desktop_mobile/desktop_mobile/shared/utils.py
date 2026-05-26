import hashlib
import xml.etree.ElementTree as ET
import json
import uuid
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import geopandas as gpd

def remove_file(path: str):
    try:
        os.remove(path)
    except Exception as e:
        print(f"Error deleting temp file {path}: {e}")

# Convert file as json
def convert_gpkg_to_geojson(tmp_path: str, layer: str = None) -> Dict[str, Any]:
    """
    Loads a GPKG, ensures GUIDs exist, and merges features with 
    sync metadata and history for cloud storage/sync.
    """
    # 1. Load the spatial layer
    gdf = gpd.read_file(tmp_path, layer=layer)
    
    # 2. Safety Check: Ensure row_guid exists. 
    # If missing, we generate them now (though they should exist in a synced layer)
    if "row_guid" not in gdf.columns:
        gdf["row_guid"] = [str(uuid.uuid4()) for _ in range(len(gdf))]
        
    # 3. Serialize GDF to GeoJSON Features list
    features_json = json.loads(gdf.to_json())

    # 4. Merge into Unified Sync Object
    merged_json = {
        "type": "FeatureCollection",
        "features": features_json.get("features", []),
    }

    return merged_json

# Write json to gpkg
def geojson_to_gpkg(geojson_data: Dict[str, Any], temp_path: str, layer: str = "features"):
    """Saves the reconstructed features back to a GPKG layer."""
    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
    # Set CRS (defaulting to 4326, adjust as needed)
    gdf.set_crs(epsg=4326, inplace=True)
    gdf.to_file(temp_path, layer=layer, driver="GPKG")
    
def convert_download_time(time_str: str) -> Optional[datetime]:
    """
    Standardizes a time string into a UTC-aware datetime object.
    """
    if not time_str:
        return None
        
    try:
        fixed_str = time_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(fixed_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None
             
# Helper function to calculate SHA-256 hash of byte data
def calculate_hash(data: bytes) -> str:
    """Calculates the SHA-256 hash of the provided bytes."""
    return hashlib.sha256(data).hexdigest()

# Helper to check if a field has changed
def field_changed(db_value, form_value):
    return form_value is not None and str(db_value) != str(form_value)
    
def normalize_qml(input_data):
    if not input_data: 
        return ""
    
    text = (input_data.get('qml_xml') or input_data.get('QML') or '') if isinstance(input_data, dict) else str(input_data)
    text = text.strip()
    
    try:
        root = ET.fromstring(text)
        for el in root.iter():
            to_remove = ["version", "id", "timestamp", "user", "projectname"]
            for attr in to_remove:
                if attr in el.attrib:
                    el.attrib.pop(attr, None)
            el.attrib = dict(sorted(el.attrib.items()))
            el[:] = sorted(el, key=lambda child: child.tag)
            
        clean_xml = ET.tostring(root, encoding='unicode', method='xml')
        return "".join(clean_xml.split())
    except Exception as e:
        print(f"Normalization failed: {e}")
        return "".join(text.split())
