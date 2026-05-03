import asyncio
import os
import sys
from sqlalchemy import select

# Add the necessary paths to sys.path
# Assuming the script is run from the root of the server
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(root_path, 'apps', 'spatial'))
sys.path.append(os.path.join(root_path, 'libs'))

# Mocking or setting up environment if needed
os.environ["MAPA_ENV"] = "DEVELOPMENT"

from spatial.config.app_container import AppContainer
from mapa.spatial.file_store.file_store_entity import FileStoreEntity

async def migrate():
    container = AppContainer()
    
    db = container.db()
    minio_service = container.minio_service()
    
    print("Starting migration...")
    
    async with db.session() as session:
        # Fetch all records with file_data
        stmt = select(FileStoreEntity).where(FileStoreEntity.file_data != None)
        result = await session.execute(stmt)
        entities = result.scalars().all()
        
        print(f"Found {len(entities)} files to migrate.")
        
        for entity in entities:
            try:
                # Use current ID and format for object name
                object_name = f"{entity.id}{entity.file_format}"
                
                print(f"Migrating {entity.id} ({entity.file_format})...")
                
                # Upload to MinIO
                minio_service.put_object(
                    object_name, 
                    entity.file_data, 
                    content_type="application/octet-stream"
                )
                
                # Update record
                entity.file_url = object_name
                # Keep file_data for safety during transition
                
                session.add(entity)
                print(f"Successfully uploaded {entity.id} to MinIO as {object_name}")
            except Exception as e:
                print(f"Failed to migrate {entity.id}: {e}")
        
        await session.commit()
        print("Migration committed to database.")

if __name__ == "__main__":
    asyncio.run(migrate())
