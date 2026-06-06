import fiona
import minio
import tempfile
import zipfile
import io
import os

def list_gdb_layers():
    try:
        # MinIO Client - try minio:9000 (Docker network)
        client = minio.Minio(
            "minio:9000",
            access_key="mapa",
            secret_key="mapa12345",
            secure=False
        )
        
        map_id = "8d66221d-d90b-4804-9200-82b6157b7543"
        bucket = "desktop-mobile"
        object_name = f"maps/{map_id}/sheet_5349_1.gdb.zip"
        
        print(f"Downloading {object_name} from MinIO...")
        response = client.get_object(bucket, object_name)
        file_bytes = response.read()
        
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
                print("Could not find .gdb folder inside zip.")
                return
                
            print(f"Found GDB path: {gdb_path}")
            layers = fiona.listlayers(gdb_path)
            print(f"GDB contains {len(layers)} layers:")
            for lyr in sorted(layers):
                print(f"  - {lyr}")
                
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_gdb_layers()
