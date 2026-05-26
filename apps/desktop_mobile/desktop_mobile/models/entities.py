from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Table, CheckConstraint, Uuid, func, UniqueConstraint
from sqlalchemy.orm import relationship
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
import uuid

# Schema specification
SCHEMA_NAME = "desktop_mobile"

# Many-to-Many Junction Tables
collection_map = Table(
    'collection_map', Base.metadata,
    Column('collection_id', Uuid(), ForeignKey(f'{SCHEMA_NAME}.collection.id', ondelete='CASCADE'), primary_key=True),
    Column('map_id', Uuid(), ForeignKey(f'{SCHEMA_NAME}.map.id', ondelete='CASCADE'), primary_key=True),
    schema=SCHEMA_NAME
)

map_layer = Table(
    'map_layer', Base.metadata,
    Column('map_id', Uuid(), ForeignKey(f'{SCHEMA_NAME}.map.id', ondelete='CASCADE'), primary_key=True),
    Column('layer_id', Uuid(), ForeignKey(f'{SCHEMA_NAME}.layer.id', ondelete='CASCADE'), primary_key=True),
    schema=SCHEMA_NAME
)

class CollectionEntity(EntityMixin, TenantMixin, Base):
    __tablename__ = "collection"
    __table_args__ = (
        UniqueConstraint('name', 'tenant_id', name='uq_collection_name_tenant'),
        {"schema": SCHEMA_NAME}
    )
    
    name = Column(String(30), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    creator = Column(String(50), nullable=True)
    updater = Column(String(50), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    maps = relationship("MapEntity", secondary=collection_map, back_populates="collections")
    
    def __repr__(self):
        return f"<Collection(id={self.id}, name='{self.name}')>"

class MapEntity(EntityMixin, TenantMixin, Base):
    __tablename__ = "map"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    name = Column(String(50), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    
    # MinIO Storage Integration: instead of storing large raw project files in PostgreSQL, 
    # we store a presigned/relative object path to MinIO (e.g. 'maps/{map_id}/project.qgz')
    project_file_url = Column(String(800), nullable=True) 
    
    creator = Column(String(50), nullable=False)  # API key ID / Username of creator
    updater = Column(String(50), nullable=False)  # API key ID / Username of last updater
    updated_at = Column(DateTime, onupdate=func.now())
    
    web_map_id = Column(Uuid(), nullable=True)  # References standard MAPA Map if linked
    
    # Relationships
    collections = relationship("CollectionEntity", secondary=collection_map, back_populates="maps")
    layers = relationship("LayerEntity", secondary=map_layer, back_populates="maps")
    
    def __repr__(self):
        return f"<Map(id={self.id}, name='{self.name}')>"

LayerFileType = [
    '.kml', '.kmz', '.shp', '.shp.zip', '.geojson', 
    '.pdf', '.gif', '.jpeg', '.jpeg.zip', '.jpg.zip', 
    '.png', '.tiff', '.tiff.zip', '.tif.zip', '.ecw', 
    '.ecw.zip', '.gdb.zip', '.mdb', '.gpkg', '.zip', '.rar'
]

class LayerEntity(EntityMixin, TenantMixin, Base):
    __tablename__ = "layer"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # kml, kmz, shp, geojson, raster formats, wms, wfs, etc.
    tags = Column(String(255), nullable=True)
    url_path = Column(String(800), nullable=True) 
    
    qml_params = Column(JSON, nullable=True)  # Layer configuration/symbology exported from QGIS
    sld_params = Column(JSON, nullable=True)  # Styling parameters as SLD
    
    creator = Column(String(50), nullable=False)
    updater = Column(String(50), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    web_layer_definition_id = Column(Uuid(), nullable=True, index=True)
    bucket = Column(String(100), nullable=True)
    
    # Relationships
    maps = relationship("MapEntity", secondary=map_layer, back_populates="layers")
    
    @property
    def has_data_source(self):
        """
        Returns True if the desktop_layer_type is one of our file-based extensions.
        """
        t = self.type.lower()
        return any(t == ext or t.endswith(ext) or ext.endswith(t) for ext in LayerFileType)

    def __repr__(self):
        return f"<Layer(id={self.id}, name='{self.name}', type='{self.type}')>"

class ApiKeyEntity(EntityMixin, TenantMixin, Base):
    __tablename__ = "api_key"
    __table_args__ = {"schema": SCHEMA_NAME}
    
    public_lookup_id = Column(String(15), nullable=False, index=True, unique=True)
    hashed_key = Column(String(128), nullable=False)
    description = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())
    
    permissions = relationship("ApiKeyPermissionEntity", back_populates="api_key", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, lookup='{self.public_lookup_id}')>"

class ApiKeyPermissionEntity(EntityMixin, TenantMixin, Base):
    __tablename__ = "apikey_permission"
    
    __table_args__ = (
        CheckConstraint(
            '(target_collection_id IS NOT NULL)::int + (target_map_id IS NOT NULL)::int + (target_layer_id IS NOT NULL)::int <= 3',
            name='check_one_target_populated'
        ),
        {"schema": SCHEMA_NAME}
    )
    
    apikey_id = Column(Uuid(), ForeignKey(f"{SCHEMA_NAME}.api_key.id", ondelete="CASCADE"), nullable=False)
    target_collection_id = Column(Uuid(), ForeignKey(f"{SCHEMA_NAME}.collection.id", ondelete='CASCADE'), nullable=True)
    target_map_id = Column(Uuid(), ForeignKey(f"{SCHEMA_NAME}.map.id", ondelete='CASCADE'), nullable=True)
    target_layer_id = Column(Uuid(), ForeignKey(f"{SCHEMA_NAME}.layer.id", ondelete='CASCADE'), nullable=True)
    access_level = Column(String(10), nullable=False, default="user")  # 'admin' or 'user'
    
    api_key = relationship("ApiKeyEntity", back_populates="permissions")
    
    def __repr__(self):
        return f"<ApiKeyPermission(id={self.id}, key_id={self.apikey_id}, level='{self.access_level}')>"
