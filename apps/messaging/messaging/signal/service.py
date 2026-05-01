import json
from uuid import UUID
from geoalchemy2.elements import WKTElement
from mapa.core.data.async_db import AsyncDatabase
from messaging.signal.repository import SignalRepository
from messaging.message.entity import SignalEntity
from sqlalchemy import text

class SignalService:
    def __init__(self, async_db: AsyncDatabase):
        self._db = async_db
        self.repo = SignalRepository(async_db)

    async def persist_signal(self, tenant_id: str, layer: str, entity_id: str, data: dict):
        lat = data.get("lat")
        lon = data.get("lon")
        
        if lat is None or lon is None:
            return

        # Create Point geometry
        wkt = f"POINT({lon} {lat})"
        
        create_dict = {
            "tenant_id": tenant_id,
            "layer": layer,
            "entity_id": entity_id,
            "geom": WKTElement(wkt, srid=4326),
            "metadata_json": json.dumps(data),
        }
        
        async with self._db.session() as session:
            if tenant_id:
                await session.execute(text(f"set app.tenant_id='{tenant_id}'"))
            
            db_obj = SignalEntity(**create_dict)
            session.add(db_obj)
            await session.commit()
