import geopandas as gpd
import fiona
import fiona.drvsupport
import tempfile
import zipfile
import io
import os
from minio import Minio

def check():
    # Minio connection
    client = Minio(
        "minio:9000",
        access_key="mapa",
        secret_key="mapa12345",
        secure=False
    )
    
    # Download the GDB zip
    # From db query, we know that for sheet_5349_1_gdb (ID: 8d66221d-d90b-4804-9200-82b6157b7543),
    # the S3 object is maps/8d66221d-d90b-4804-9200-82b6157b7543/sheet_5349_1.gdb.zip
    bucket = "desktop-mobile"
    object_name = "maps/8d66221d-d90b-4804-9200-82b6157b7543/sheet_5349_1.gdb.zip"
    
    response = client.get_object(bucket, object_name)
    file_bytes = response.read()
    response.close()
    
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
                
        print("GDB Path:", gdb_path)
        
        # Open notes layer
        gdf = gpd.read_file(gdb_path, layer="notes")
        print("\nColumns and Dtypes:")
        print(gdf.dtypes)
        
        print("\nFirst row values:")
        if not gdf.empty:
            print(gdf.iloc[0])
            
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    check()
