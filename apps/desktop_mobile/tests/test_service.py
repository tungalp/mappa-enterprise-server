import pytest
from desktop_mobile.config.app_container import AppContainer
from desktop_mobile.models.schemas import CollectionCreate, MapCreate, LayerCreate
from desktop_mobile.services.auth import generate_key_data

def test_container_initialization():
    """Verifies that the dependency injection container starts up and maps successfully."""
    container = AppContainer()
    assert container is not None
    assert container.config is not None
    assert container.db is not None
    assert container.minio_service is not None

def test_pydantic_schemas_validation():
    """Verifies validation logic in Pydantic schemas."""
    # Test Collection Schema
    col = CollectionCreate(name="Base Topo Maps", description="QGIS background layer collection")
    assert col.name == "Base Topo Maps"
    assert col.description == "QGIS background layer collection"

    # Test Map Schema Validation (Whitespace checking)
    with pytest.raises(ValueError, match="Name cannot be empty or whitespace only"):
        MapCreate(name="   ", description="Invalid map name")

    # Test Layer Schema
    layer = LayerCreate(name="roads", type="geojson", tags="transport,base")
    assert layer.name == "roads"
    assert layer.type == "geojson"

def test_cryptographic_key_generation():
    """Verifies the key generation function generates keys with expected prefixes and lengths."""
    raw_key, lookup_id, hashed_key = generate_key_data()
    
    assert raw_key.startswith("pk_")
    assert len(raw_key) == 32
    assert len(lookup_id) == 15
    assert lookup_id == raw_key[:15]
    assert hashed_key is not None
