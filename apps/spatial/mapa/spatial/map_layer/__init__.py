# models/__init__.py
from mapa.spatial.map.map_model import Map
from mapa.spatial.map_layer.map_layer_model import MapLayer
from mapa.spatial.map_base_layer.map_base_layer_model import MapBaseLayer

# Resolve circular dependencies
MapBaseLayer.model_rebuild()
MapLayer.model_rebuild()
Map.model_rebuild()

# Export models for clean imports
__all__ = ['Map', 'MapLayer', 'MapBaseLayer']