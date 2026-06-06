import sys
import os
import uuid
import json

# Add apps/desktop_mobile to path
sys.path.insert(0, '/workspace/apps/desktop_mobile')

from desktop_mobile.shared.utils import extract_layer_groups
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from desktop_mobile.models.entities import LayerEntity, MapEntity

# Create database engine
engine = create_engine('postgresql://postgres:postgres@postgres/mapa_test')
Session = sessionmaker(bind=engine)
session = Session()

try:
    map_id = "8d66221d-d90b-4804-9200-82b6157b7543"
    qgs_path = f"/workspace/scratch/qgis-projects/{map_id}.qgs"
    
    # 1. Fetch all layers
    all_layers = session.query(LayerEntity).all()
    print("Total layers in DB:", len(all_layers))
    
    # 2. Build layers_lookup mapping filenames and names
    layers_lookup = {}
    for layer in all_layers:
        if layer.url_path:
            clean_url_path = layer.url_path.split('|')[0]
            if clean_url_path:
                fn = os.path.basename(clean_url_path).lower()
                layers_lookup[fn] = layer
        if layer.name:
            layers_lookup[layer.name.lower()] = layer
            
    # 3. Read QGS XML file
    with open(qgs_path, 'rb') as f:
        qgs_xml_bytes = f.read()
        
    # 4. Extract layer groups using the updated utils.py
    groups = extract_layer_groups(qgs_xml_bytes, layers_lookup)
    print("Extracted groups count:", len(groups))
    print("Sample groups:")
    for k, v in list(groups.items())[:10]:
        print(f"  Layer ID: {k} -> Group: {v}")
    
    # 5. Save to map entity
    db_map = session.query(MapEntity).filter(MapEntity.id == uuid.UUID(map_id)).first()
    if db_map:
        db_map.layer_groups = groups
        session.commit()
        print("Successfully updated layer_groups in DB for map:", db_map.name)
    else:
        print("Map not found in DB!")

except Exception as e:
    session.rollback()
    print("Error:", e)
finally:
    session.close()
