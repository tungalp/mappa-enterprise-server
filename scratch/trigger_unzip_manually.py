import uuid
import sys
import os

# Set PYTHONPATH programmatically
sys.path.insert(0, "/workspace")
sys.path.insert(0, "/workspace/apps/desktop_mobile")
sys.path.insert(0, "/workspace/libs/core")

from desktop_mobile.config.app_container import AppContainer

def run_unzip_test():
    container = AppContainer()
    layer_service = container.layer_service()
    minio = container.minio_service()
    
    # Let's test for: mozambique-thematic-300k.tif.zip
    layer_id = uuid.UUID("c6b5147a-1e7a-4479-bdda-7b0f3726e202")
    url_path = "layers/c6b5147a-1e7a-4479-bdda-7b0f3726e202/mozambique-thematic-300k.tif.zip"
    bucket = "desktop-mobile"
    
    print(f"Downloading {url_path} from MinIO...")
    try:
        file_bytes = minio.get_object(url_path, bucket=bucket)
        print("Success! File size:", len(file_bytes))
        
        print("Triggering unzipper...")
        layer_service._upload_unzipped_files("mozambique-thematic-300k.tif.zip", file_bytes, layer_id, bucket, url_path)
        print("Done!")
    except Exception as e:
        print("Error during TIFF unzip:", e)

    # Let's test for: sheet_5349_1.gdb.zip
    layer_id_gdb = uuid.UUID("9f1159f4-4b01-4b68-9bbe-8deeacd3db60")
    url_path_gdb = "layers/9f1159f4-4b01-4b68-9bbe-8deeacd3db60/sheet_5349_1.gdb.zip"
    
    print(f"\nDownloading {url_path_gdb} from MinIO...")
    try:
        file_bytes_gdb = minio.get_object(url_path_gdb, bucket=bucket)
        print("Success! File size:", len(file_bytes_gdb))
        
        print("Triggering unzipper...")
        layer_service._upload_unzipped_files("sheet_5349_1.gdb.zip", file_bytes_gdb, layer_id_gdb, bucket, url_path_gdb)
        print("Done!")
    except Exception as e:
        print("Error during GDB unzip:", e)

if __name__ == "__main__":
    run_unzip_test()
