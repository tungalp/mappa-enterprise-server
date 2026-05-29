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

def get_base_filename(fn: str) -> str:
    fn = fn.lower()
    for ext in ['.zip', '.gdb', '.shp', '.geojson', '.tif', '.tiff', '.kml', '.kmz', '.gpkg']:
        if fn.endswith(ext):
            fn = fn[:-len(ext)]
    return fn

def process_qgs_xml(xml_data: bytes, layers_lookup: dict) -> bytes:
    """
    Parses and rewrites datasource paths inside raw QGS XML data.
    """
    import xml.etree.ElementTree as ET
    import os

    # Build a base-name lookup mapping (e.g., "sheet_5349_1" -> Layer)
    base_layers_lookup = {}
    for clean_fn, layer in layers_lookup.items():
        base_layers_lookup[get_base_filename(clean_fn)] = layer
        # Support fallback GDB sub-layer matching using layer name directly
        if layer.name:
            base_layers_lookup[layer.name.lower()] = layer

    try:
        xml_str = xml_data.decode('utf-8')
        root = ET.fromstring(xml_str)
    except Exception as e:
        print(f"[QGS Rewrite] XML parsing failed: {e}")
        return xml_data
        
    modified = False
    # Find all <datasource> elements
    for ds in root.findall(".//datasource"):
        if ds.text:
            ds_text = ds.text
            # Split query parameters if any (e.g. |layername=xxx)
            if '|' in ds_text:
                file_part, query_part = ds_text.split('|', 1)
                query_part = '|' + query_part
            else:
                file_part = ds_text
                query_part = ''
            
            # Extract layername from query_part if present for GDB matching fallback
            layername_fallback = None
            if "layername=" in query_part:
                layername_fallback = query_part.split("layername=")[1].split("&")[0].lower()

            # Replace backslashes with forward slashes for unified path handling
            normalized_path = file_part.replace('\\', '/')
            filename = os.path.basename(normalized_path)
            filename_lower = filename.lower()
            
            # Check base filename or layer name matching
            base_fn = get_base_filename(filename_lower)
            layer = None
            if base_fn in base_layers_lookup:
                layer = base_layers_lookup[base_fn]
            elif layername_fallback in base_layers_lookup:
                layer = base_layers_lookup[layername_fallback]
                
            if layer:
                t_lower = layer.type.lower()
                # ONLY rewrite if it is a file-based layer. Service/database layers (wfs, wms, wmts, wcs, postgres, mssql, oracle, arcgismapserver) must not be rewritten.
                if t_lower in ('wfs', 'wms', 'wmts', 'wcs', 'postgres', 'mssql', 'oracle', 'arcgismapserver'):
                    continue

                bucket = layer.bucket or "desktop-mobile"
                
                # Formulate the correct unzipped/raw path for vsis3
                clean_url_path = layer.url_path.split('|')[0] if layer.url_path else ""
                s3_folder = clean_url_path.rsplit('/', 1)[0] if '/' in clean_url_path else f"layers/{layer.id}"
                
                is_zipped_upload = clean_url_path.lower().endswith(".zip") and t_lower != ".zip"
                if is_zipped_upload:
                    # Zipped upload for an unzipped layer source -> point to the extracted file/folder in S3
                    vsis3_path = f"/vsis3/{bucket}/{s3_folder}/{filename_lower}"
                else:
                    # Natively zipped or standard unzipped files -> point to the registered S3 url_path
                    vsis3_path = f"/vsis3/{bucket}/{layer.url_path}"
                    
                new_ds_text = f"{vsis3_path}{query_part}"
                print(f"[QGZ Rewrite] Replacing '{ds_text}' with '{new_ds_text}'")
                ds.text = new_ds_text
                modified = True
                
    if modified:
        return ET.tostring(root, encoding='utf-8')
    return xml_data

def process_qgz_project(file_data: bytes, layers_lookup: dict, is_qgs: bool = False) -> bytes:
    """
    Saves incoming project bytes to a temp file, extracts and processes the .qgs XML
    inside, replaces file-based layers with their correct /vsis3 paths, re-zips it,
    and returns the modified bytes. If is_qgs is True, processes the raw XML directly.
    """
    if is_qgs:
        return process_qgs_xml(file_data, layers_lookup)

    import tempfile
    import zipfile
    import os

    # Write file_data to a temporary file
    temp_in_fd, temp_in_path = tempfile.mkstemp(suffix=".qgz")
    temp_out_fd, temp_out_path = tempfile.mkstemp(suffix=".qgz")
    
    try:
        with os.fdopen(temp_in_fd, 'wb') as f:
            f.write(file_data)
            
        # Extract and process zip contents
        with zipfile.ZipFile(temp_in_path, 'r') as zip_in:
            with zipfile.ZipFile(temp_out_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                for item in zip_in.infolist():
                    data = zip_in.read(item.filename)
                    if item.filename.lower().endswith('.qgs'):
                        data = process_qgs_xml(data, layers_lookup)
                            
                    zip_out.writestr(item.filename, data)
                    
        # Read the modified zip file back
        with open(temp_out_path, 'rb') as f:
            modified_bytes = f.read()
            
        return modified_bytes
        
    finally:
        # Clean up temporary files safely
        for path in (temp_in_path, temp_out_path):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"Error removing temp file {path}: {e}")

