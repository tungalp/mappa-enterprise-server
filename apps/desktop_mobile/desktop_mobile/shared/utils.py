import hashlib
import xml.etree.ElementTree as ET
import json
import uuid
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import geopandas as gpd

def rewrite_presigned_url(request, original_url: str) -> str:
    """Rewrites 'localhost' in presigned Minio URLs with the actual requesting client's IP."""
    import urllib.parse
    host_header = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if host_header:
        host_ip = host_header.split(":")[0]
        if host_ip not in ["localhost", "127.0.0.1"]:
            parsed = urllib.parse.urlparse(original_url)
            if parsed.hostname in ["localhost", "127.0.0.1"]:
                new_netloc = f"{host_ip}:{parsed.port}" if parsed.port else host_ip
                return parsed._replace(netloc=new_netloc).geturl()
    return original_url

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
        l_name = getattr(layer, 'name', None)
        if l_name:
            base_layers_lookup[l_name.lower()] = layer

    try:
        xml_str = xml_data.decode('utf-8')
        root = ET.fromstring(xml_str)
    except Exception as e:
        print(f"[QGS Rewrite] XML parsing failed: {e}")
        return xml_data
        
    modified = False
    # 1. Find all <datasource> elements
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
                l_type = getattr(layer, 'type', '')
                t_lower = l_type.lower() if l_type else ''
                # ONLY rewrite if it is a file-based layer. Service/database layers (wfs, wms, wmts, wcs, postgres, mssql, oracle, arcgismapserver) must not be rewritten.
                if t_lower in ('wfs', 'wms', 'wmts', 'wcs', 'postgres', 'mssql', 'oracle', 'arcgismapserver'):
                    continue

                bucket = getattr(layer, 'bucket', None) or "desktop-mobile"
                
                # Formulate the correct unzipped/raw path for vsis3
                l_url_path = getattr(layer, 'url_path', None) or ""
                clean_url_path = l_url_path.split('|')[0] if l_url_path else ""
                l_id = getattr(layer, 'id', None) or "unknown"
                s3_folder = clean_url_path.rsplit('/', 1)[0] if '/' in clean_url_path else f"layers/{l_id}"
                
                is_zipped_upload = clean_url_path.lower().endswith(".zip") and t_lower != ".zip"
                if is_zipped_upload:
                    # Zipped upload for an unzipped layer source -> point to the extracted file/folder in S3
                    vsis3_path = f"/vsis3/{bucket}/{s3_folder}/{filename_lower}"
                else:
                    # Natively zipped or standard unzipped files -> point to the registered S3 url_path
                    vsis3_path = f"/vsis3/{bucket}/{l_url_path}"
                    
                new_ds_text = f"{vsis3_path}{query_part}"
                print(f"[QGZ Rewrite] Replacing datasource '{ds_text}' with '{new_ds_text}'")
                ds.text = new_ds_text
                modified = True

    # 2. Find all <layer-tree-layer> elements and rewrite their source attributes
    for ltl in root.findall(".//layer-tree-layer"):
        ds_text = ltl.get("source")
        if ds_text:
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
                l_type = getattr(layer, 'type', '')
                t_lower = l_type.lower() if l_type else ''
                # ONLY rewrite if it is a file-based layer. Service/database layers (wfs, wms, wmts, wcs, postgres, mssql, oracle, arcgismapserver) must not be rewritten.
                if t_lower in ('wfs', 'wms', 'wmts', 'wcs', 'postgres', 'mssql', 'oracle', 'arcgismapserver'):
                    continue

                bucket = getattr(layer, 'bucket', None) or "desktop-mobile"
                
                # Formulate the correct unzipped/raw path for vsis3
                l_url_path = getattr(layer, 'url_path', None) or ""
                clean_url_path = l_url_path.split('|')[0] if l_url_path else ""
                l_id = getattr(layer, 'id', None) or "unknown"
                s3_folder = clean_url_path.rsplit('/', 1)[0] if '/' in clean_url_path else f"layers/{l_id}"
                
                is_zipped_upload = clean_url_path.lower().endswith(".zip") and t_lower != ".zip"
                if is_zipped_upload:
                    # Zipped upload for an unzipped layer source -> point to the extracted file/folder in S3
                    vsis3_path = f"/vsis3/{bucket}/{s3_folder}/{filename_lower}"
                else:
                    # Natively zipped or standard unzipped files -> point to the registered S3 url_path
                    vsis3_path = f"/vsis3/{bucket}/{l_url_path}"
                    
                new_ds_text = f"{vsis3_path}{query_part}"
                print(f"[QGZ Rewrite] Replacing layer-tree-layer source '{ds_text}' with '{new_ds_text}'")
                ltl.set("source", new_ds_text)
                modified = True
                
    if modified:
        return ET.tostring(root, encoding='utf-8')
    return xml_data

def extract_layer_groups(qgs_xml_bytes: bytes, layers_lookup: dict) -> dict:
    """
    Parses QGIS XML project data, finds all maplayer IDs and matches them to LayerEntity database IDs.
    Then, traverses the layer-tree-group hierarchy to determine the group path/name of each layer.
    Returns a dictionary of {str(layer_uuid): group_path}.
    """
    import xml.etree.ElementTree as ET
    import os
    
    # 1. Build a lookup of base filename / name -> LayerEntity
    base_layers_lookup = {}
    for clean_fn, layer in layers_lookup.items():
        base_layers_lookup[get_base_filename(clean_fn)] = layer
        l_name = getattr(layer, 'name', None)
        if l_name:
            base_layers_lookup[l_name.lower()] = layer

    try:
        xml_str = qgs_xml_bytes.decode('utf-8')
        root = ET.fromstring(xml_str)
    except Exception as e:
        print(f"[QGS Extract Groups] XML parsing failed: {e}")
        return {}

    # 2. Map QGIS maplayer ID -> LayerEntity UUID
    qgis_to_db_map = {}
    for maplayer in root.findall(".//projectlayers/maplayer"):
        id_el = maplayer.find("id")
        qgis_id = maplayer.get("id") or (id_el.text if id_el is not None else None)
        if not qgis_id:
            continue
            
        datasource = maplayer.find("datasource")
        layername = maplayer.find("layername")
        
        ds_text = datasource.text if datasource is not None and datasource.text else ""
        layername_text = layername.text if layername is not None and layername.text else ""
        
        # Extract layername from query if present
        layername_fallback = None
        if '|' in ds_text:
            file_part, query_part = ds_text.split('|', 1)
            if "layername=" in query_part:
                layername_fallback = query_part.split("layername=")[1].split("&")[0].lower()
        else:
            file_part = ds_text
            
        # Replace backslashes with forward slashes
        normalized_path = file_part.replace('\\', '/')
        filename = os.path.basename(normalized_path)
        filename_lower = filename.lower()
        
        base_fn = get_base_filename(filename_lower)
        
        # Match using base_fn, fallback layer name, or layername child
        layer = None
        if base_fn in base_layers_lookup:
            layer = base_layers_lookup[base_fn]
        elif layername_fallback in base_layers_lookup:
            layer = base_layers_lookup[layername_fallback]
        elif layername_text.lower() in base_layers_lookup:
            layer = base_layers_lookup[layername_text.lower()]
            
        if layer:
            l_id = getattr(layer, 'id', None)
            if l_id:
                qgis_to_db_map[qgis_id] = str(l_id)

    # 3. Traverse layer-tree-group recursively
    layer_groups = {}
    
    # We find the main layer-tree-group (usually the first level)
    root_group = root.find(".//layer-tree-group")
    
    def traverse_group(group_el, parent_path):
        # The name of this group is in the 'name' attribute
        group_name = group_el.get("name")
        current_path = parent_path + [group_name] if group_name else parent_path
        
        # Look for child layer-tree-group elements
        for child_group in group_el.findall("./layer-tree-group"):
            traverse_group(child_group, current_path)
            
        # Look for child layer-tree-layer elements
        for child_layer in group_el.findall("./layer-tree-layer"):
            qgis_id = child_layer.get("id")
            if qgis_id in qgis_to_db_map:
                db_id = qgis_to_db_map[qgis_id]
                if current_path:
                    layer_groups[db_id] = "/".join(current_path)

    if root_group is not None:
        # Traverse from root group
        for child_group in root_group.findall("./layer-tree-group"):
            traverse_group(child_group, [])
        for child_layer in root_group.findall("./layer-tree-layer"):
            qgis_id = child_layer.get("id")
            if qgis_id in qgis_to_db_map:
                db_id = qgis_to_db_map[qgis_id]
                # Root level layers have no group
                layer_groups[db_id] = ""
                
    return layer_groups

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

def extract_and_convert_extent(qgs_xml_bytes: bytes) -> Optional[List[float]]:
    """
    Parses QGIS XML project data, harvests the project map canvas extent andauthid,
    and converts the bounds to standard WGS84 [minLng, minLat, maxLng, maxLat].
    """
    import xml.etree.ElementTree as ET
    import math
    
    try:
        xml_str = qgs_xml_bytes.decode('utf-8')
        root = ET.fromstring(xml_str)
    except Exception as e:
        print(f"[QGS Extent] Failed to decode/parse XML: {e}")
        return None
        
    try:
        extent_el = root.find(".//mapcanvas/extent")
        if extent_el is None:
            print("[QGS Extent] mapcanvas/extent not found in project XML.")
            return None
            
        xmin = float(extent_el.find("xmin").text)
        ymin = float(extent_el.find("ymin").text)
        xmax = float(extent_el.find("xmax").text)
        ymax = float(extent_el.find("ymax").text)
        
        # Get authid (SRS)
        authid = "EPSG:4326"
        authid_el = root.find(".//mapcanvas/destinationsrs/spatialrefsys/authid")
        if authid_el is not None and authid_el.text:
            authid = authid_el.text.strip().upper()
        else:
            proj_el = root.find(".//projectionparameters/destinationsrs/spatialrefsys/authid")
            if proj_el is not None and proj_el.text:
                authid = proj_el.text.strip().upper()
                
        print(f"[QGS Extent] Extracted raw bounds: [{xmin}, {ymin}, {xmax}, {ymax}] CRS={authid}")
        
        if authid == "EPSG:4326":
            return [xmin, ymin, xmax, ymax]
            
        # Reproject from authid to WGS84 (EPSG:4326)
        try:
            import pyproj
            transformer = pyproj.Transformer.from_crs(authid, "EPSG:4326", always_xy=True)
            sw_lng, sw_lat = transformer.transform(xmin, ymin)
            ne_lng, ne_lat = transformer.transform(xmax, ymax)
            return [sw_lng, sw_lat, ne_lng, ne_lat]
        except Exception as proj_err:
            print(f"[QGS Extent] Pyproj conversion failed: {proj_err}. Trying fallback math...")
            
            # Simple fallback for Web Mercator (EPSG:3857) to WGS84
            if authid == "EPSG:3857" or authid == "EPSG:900913":
                def to_wgs84(x, y):
                    lng = (x / 6378137.0) * (180.0 / math.pi)
                    lat = (2.0 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2.0) * (180.0 / math.pi)
                    return lng, lat
                sw_lng, sw_lat = to_wgs84(xmin, ymin)
                ne_lng, ne_lat = to_wgs84(xmax, ymax)
                return [sw_lng, sw_lat, ne_lng, ne_lat]
            else:
                print(f"[QGS Extent] Unsupported projection fallback: {authid}")
                return None
    except Exception as e:
        print(f"[QGS Extent] Failed to extract bounds: {e}")
        
    return None


