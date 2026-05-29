from osgeo import ogr
import os

def test_open():
    # Set S3 environment variables so GDAL can authenticate
    os.environ["AWS_S3_ENDPOINT"] = "minio:9000"
    os.environ["AWS_ACCESS_KEY_ID"] = "mapa"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "mapa12345"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["AWS_HTTPS"] = "NO"
    os.environ["AWS_VIRTUAL_HOSTING"] = "FALSE"
    os.environ["AWS_VIRTUAL_HOST_STYLE"] = "FALSE"
    os.environ["CPL_DEBUG"] = "ON"  # Turn on GDAL verbose debug logs!

    gdb_path = "/vsis3/desktop-mobile/layers/9f1159f4-4b01-4b68-9bbe-8deeacd3db60/sheet_5349_1.gdb"
    print(f"Attempting to open GDB via GDAL/OGR:\n{gdb_path}\n")
    
    ogr.UseExceptions()
    try:
        ds = ogr.Open(gdb_path)
        if ds is None:
            print("Failed to open GDB (returned None)")
        else:
            print("SUCCESS! Opened GDB.")
            print(f"Layer Count: {ds.GetLayerCount()}")
            print("Layers:")
            for i in range(min(5, ds.GetLayerCount())):
                lyr = ds.GetLayer(i)
                print(f"  - {lyr.GetName()} ({lyr.GetFeatureCount()} features)")
    except Exception as e:
        print(f"OGR Open Exception: {e}")

if __name__ == "__main__":
    test_open()
