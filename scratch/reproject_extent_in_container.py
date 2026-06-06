import os
import xml.etree.ElementTree as ET
import psycopg2
import json
import pyproj

def to_wgs84(xmin, ymin, xmax, ymax, from_epsg):
    print(f"Reprojecting from {from_epsg} to EPSG:4326...")
    transformer = pyproj.Transformer.from_crs(from_epsg, "EPSG:4326", always_xy=True)
    sw_lng, sw_lat = transformer.transform(xmin, ymin)
    ne_lng, ne_lat = transformer.transform(xmax, ymax)
    return [sw_lng, sw_lat, ne_lng, ne_lat]

def parse_extent(qgs_path):
    if not os.path.exists(qgs_path):
        print(f"File not found: {qgs_path}")
        return None
        
    try:
        tree = ET.parse(qgs_path)
        root = tree.getroot()
        
        extent_el = root.find(".//mapcanvas/extent")
        if extent_el is None:
            print(f"Extent not found in {qgs_path}")
            return None
            
        xmin = float(extent_el.find("xmin").text)
        ymin = float(extent_el.find("ymin").text)
        xmax = float(extent_el.find("xmax").text)
        ymax = float(extent_el.find("ymax").text)
        
        # Get authid
        authid = "EPSG:4326"
        authid_el = root.find(".//mapcanvas/destinationsrs/spatialrefsys/authid")
        if authid_el is not None and authid_el.text:
            authid = authid_el.text.strip().upper()
        else:
            proj_el = root.find(".//projectionparameters/destinationsrs/spatialrefsys/authid")
            if proj_el is not None and proj_el.text:
                authid = proj_el.text.strip().upper()
                
        print(f"Parsed {os.path.basename(qgs_path)}: Extent=[{xmin}, {ymin}, {xmax}, {ymax}] CRS={authid}")
        
        if authid == "EPSG:4326":
            return [xmin, ymin, xmax, ymax]
            
        return to_wgs84(xmin, ymin, xmax, ymax, authid)
    except Exception as e:
        print(f"Failed to parse XML {qgs_path}: {e}")
    return None

def main():
    db_config = {
        "host": "postgres",
        "port": 5432,
        "dbname": "mapa_test",
        "user": "postgres",
        "password": "postgres"
    }
    
    qgs_path = "/workspace/scratch/qgis-projects/8d66221d-d90b-4804-9200-82b6157b7543.qgs"
    bounds = parse_extent(qgs_path)
    if bounds:
        print(f"WGS84 Bounds: {bounds}")
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE desktop_mobile.map SET initial_bounds = %s WHERE id = '8d66221d-d90b-4804-9200-82b6157b7543';",
                (json.dumps(bounds),)
            )
            conn.commit()
            print("Successfully updated initial_bounds for sheet_5349_1_gdb!")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
    else:
        print("Could not compute bounds.")

if __name__ == "__main__":
    main()
