import asyncio
import sys
import uuid
import os

# Set PYTHONPATH programmatically
sys.path.insert(0, "/workspace")
sys.path.insert(0, "/workspace/apps/desktop_mobile")
sys.path.insert(0, "/workspace/libs/core")

from desktop_mobile.config.app_container import AppContainer

async def rewrite_project():
    container = AppContainer()
    map_service = container.map_service()
    minio = container.minio_service()
    
    map_id = uuid.UUID("8d66221d-d90b-4804-9200-82b6157b7543")
    
    # 1. Fetch existing Map record
    async with map_service.repo._db.session() as session:
        from desktop_mobile.models.entities import MapEntity
        from sqlalchemy import select
        stmt = select(MapEntity).where(MapEntity.id == map_id)
        res = await session.execute(stmt)
        db_map = res.scalars().first()
        if not db_map:
            print("Map not found!")
            return
        
        project_file_url = db_map.project_file_url
        print(f"Current project_file_url in DB: {project_file_url}")
        
    # 2. Download original project file from MinIO
    print("Downloading project file from MinIO...")
    bucket = "desktop-mobile"
    file_bytes = None
    actual_file_name = "project.qgz"
    
    # Try downloading the DB's url first
    try:
        file_bytes = minio.get_object(project_file_url, bucket=bucket)
        actual_file_name = project_file_url.split("/")[-1]
        print(f"Success! Downloaded {project_file_url} (size: {len(file_bytes)})")
    except Exception as e:
        print(f"Could not download {project_file_url}, trying alternative .qgs extension: {e}")
        alt_url = project_file_url.replace('.qgz', '.qgs')
        try:
            file_bytes = minio.get_object(alt_url, bucket=bucket)
            actual_file_name = alt_url.split("/")[-1]
            print(f"Success! Downloaded {alt_url} (size: {len(file_bytes)})")
        except Exception as alt_e:
            print("Failed to download both extensions:", alt_e)
            return
        
    # 3. Trigger upload_project_file (which runs the rewriter)
    print(f"Triggering upload_project_file with name '{actual_file_name}' to rewrite datasource paths...")
    try:
        updated_map = await map_service.upload_project_file(
            map_id=map_id,
            file_name=actual_file_name,
            file_data=file_bytes,
            user_id="manual_fix"
        )
        print("Success! Project file rewritten and uploaded.")
        print(f"Accompanied QGS saved at /workspace/scratch/qgis-projects/{map_id}.qgs")
    except Exception as e:
        print("Error during rewrite/upload:", e)

if __name__ == "__main__":
    asyncio.run(rewrite_project())
