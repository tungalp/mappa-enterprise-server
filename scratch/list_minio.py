from desktop_mobile.config.app_container import AppContainer
container = AppContainer()
minio = container.minio_service()
prefix = ""
print(f"Listing objects under bucket 'desktop-mobile', prefix '{prefix}':")
try:
    objects = minio.list_objects(prefix, bucket="desktop-mobile")
    unique_zips = set()
    unique_gdbs = set()
    for obj in objects:
        name = obj.object_name
        if ".gdb.zip" in name:
            unique_zips.add(name)
        elif ".gdb/" in name:
            parts = name.split(".gdb/")
            unique_gdbs.add(parts[0] + ".gdb/")
        elif ".tif" in name:
            unique_zips.add(name)
        elif ".qgz" in name or ".qgs" in name:
            unique_zips.add(name)
            
    print("Unique Zipped / Direct Upload Paths on S3:")
    for path in sorted(unique_zips):
        print(f"  - {path}")
    print("\nUnique Unzipped GDB Folders on S3:")
    for path in sorted(unique_gdbs):
        print(f"  - {path}")
except Exception as e:
    print("Error listing:", e)
