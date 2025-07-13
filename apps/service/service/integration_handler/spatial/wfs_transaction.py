from enum import Enum
from typing import Any, Dict, List
from lxml import etree
from pygml.v32 import encode_v32, GeomDict
from mapa.core.data.query_args import QueryArgs
from mapa.gateway.integration.integration_model import  SpatialServerType
from shapely.geometry import MultiPolygon, Polygon, shape, mapping
from service.integration_handler.spatial.transform_to_ogc import TransformToOGC
from shapely.ops import unary_union, transform
from pyproj import Transformer,Proj

class WFSOperationType(Enum):
    INSERT = "Insert"
    UPDATE = "Update"
    DELETE = "Delete"
    
class GeometryType(Enum):   
    Point = 'Point'
    LineString = 'LineString'
    Polygon = 'Polygon'
    MultiPoint = 'MultiPoint'
    MultiLineString = 'MultiLineString'
    MultiPolygon = 'MultiPolygon'
    Geometry = 'Geometry'

class WfsTransaction:
    """WFS Transaction service"""

    # Define the namespaces
    DEFAULT_NS_MAP = {
        "wfs": "http://www.opengis.net/wfs/2.0",
        "gml": "http://www.opengis.net/gml/3.2",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "fes": 'http://www.opengis.net/fes/2.0'
    }

    # Attribs
    VERSION = "2.0.0"
    SERVICE = "WFS"
    DEFAULT_EPSG =  "EPSG:4326"

    # target_proj bilgisi özellikle Arcgis için eklenmiştir.
    # insert update işlemleri işlem yapılmak istenen geometrinin X/Y coordinat bilgileri ters işlenmektedir.
    # Bu tersliği çözebilimek için ilgili geometriyi encode_v32 yapmadan önce geometrinin crs bilgisi ilgili target_proj bilgisine göre set edilmektedir.
    # (03.07.2024)
    def __init__(self, ns_url: str | None = None, geometry_name: str="geom", server_type: str | None = None, target_proj: str | None = None) -> None:
        self._ns_url = ns_url
        self._geometry_name = geometry_name
        self._server_type = server_type
        self._target_proj = target_proj
        self._transformer = TransformToOGC()
    
    def insert(self, type_name: str, features: List[Dict[str, Any]]) -> str:
        full_name = self._split_type_name(type_name)
        ns_map = self.DEFAULT_NS_MAP.copy()
        ns_key = full_name["namespace"]
        ns_map[ns_key] = f"{self._ns_url or full_name['namespace']}"
        attrib={"version": self.VERSION, "service": self.SERVICE}

        root = etree.Element("{%s}Transaction" % ns_map["wfs"], attrib, ns_map)
        op_el = etree.SubElement(root, f"{{{ns_map['wfs']}}}{WFSOperationType.INSERT.value}", {}, {})
        
        index = 1
        for feat in features:
            self._create_feature_element(op_el, ns_map[ns_key], full_name["name"], feat, index)
            index += 1

        return etree.tostring(root, encoding="utf-8").decode('utf-8')
    
    def update(self, type_name: str, feature: Dict[str, Any], query_args: QueryArgs) -> str:
        ns_map = self.DEFAULT_NS_MAP.copy()
        attrib={"version": self.VERSION, "service": self.SERVICE}

        root = etree.Element("{%s}Transaction" % ns_map["wfs"], attrib, ns_map)
        op_el = etree.SubElement(root, f"{{{ns_map['wfs']}}}{WFSOperationType.UPDATE.value}", {
            "typeName": type_name
        }, {})
        
        index = 1
        # Properties        
        properties = feature.get("properties")
        if properties:
            for field, value in properties.items():
                prop_el = etree.SubElement(op_el, f"{{{ns_map['wfs']}}}Property", {}, {})
                etree.SubElement(prop_el, f"{{{ns_map['wfs']}}}ValueReference", {}, {}).text = field
                etree.SubElement(prop_el, f"{{{ns_map['wfs']}}}Value", {}, {}).text = str(value)
            index += 1

        # Geometry
        geometry = feature.get("geometry")
        if (geometry):
            id = feature.get("id") or str(f"{type_name}.{index}")
            geom_field_name = feature.get("geometry_name") or self._geometry_name
            prop_el = etree.SubElement(op_el, f"{{{ns_map['wfs']}}}Property", {}, {})
            etree.SubElement(prop_el, f"{{{ns_map['wfs']}}}ValueReference", {}, {}).text = geom_field_name
            
            # Not : Arcgis'e insert işleminde X/Y bilgilerinin ters olmasından dolayı geometrinin default crs bilgisi (CRS84) yerine
            # Katmanın SRID bilgisi set edilmiştir. Bu sayede encode_v32 işlemi sırasında X/Y bilgilerini kendisi otomatik değiştirmektedir.
            # Ayrıca MultiSurface kısımlarında hata ile karşılaşıldığı için sadece Arcgis tarafında,
            # gelen MultiPolygon tipleri Polygon'a çevrilmiştir. (05.07.2024)
            
            if self._server_type == SpatialServerType.ArcGIS and self._target_proj is not None:
                geometry["crs"] = {"type": "name","properties": {"name": self._target_proj}}
                
                if geometry['type'] == GeometryType.MultiPolygon.value:
                    geometry = self._to_polygon(geometry)
                    
            if self._target_proj != self.DEFAULT_EPSG:
                geometry = self._projection(geometry)           
                
            geom_el = encode_v32(geometry, id)
            value_el = etree.SubElement(prop_el, f"{{{ns_map['wfs']}}}Value", {}, {})
            value_el.append(geom_el)

        ogc_filter = self._transformer.transform(query_args)
        op_el.append(ogc_filter)

        return etree.tostring(root, encoding="utf-8").decode('utf-8')
    
    def delete(self, type_name: str, query_args: QueryArgs) -> str:
        ns_map = self.DEFAULT_NS_MAP.copy()
        attrib={"version": self.VERSION, "service": self.SERVICE}

        root = etree.Element("{%s}Transaction" % ns_map["wfs"], attrib, ns_map)
        op_el = etree.SubElement(root, f"{{{ns_map['wfs']}}}{WFSOperationType.DELETE.value}", {
            "typeName": type_name
        }, {})
        
        ogc_filter = self._transformer.transform(query_args)
        op_el.append(ogc_filter)

        return etree.tostring(root, encoding="utf-8").decode('utf-8')
    
    def _split_type_name(self, type_name: str) -> Dict[str, str]:
        if (type_name.find(":") == -1):
            raise ValueError('Typename must include namespace')
        type_name_parts = type_name.split(":")
        return {
            "namespace": type_name_parts[0],
            "name": type_name_parts[1]
        }

    def _create_feature_element(self, parent: Any, ns: str, type_name: str, feature: Dict[str, Any], index: int):
        if str(feature["type"]).lower() != 'feature':
            raise ValueError('Geojson type must be feature')

        # Properties
        feat_el = etree.SubElement(parent, f"{{{ns}}}{type_name}", {}, {})
        properties = feature.get("properties")
        if properties:
            for field, value in properties.items():
                field_el = etree.SubElement(feat_el, f"{{{ns}}}{field}", {}, {})
                field_el.text = str(value)

        # Geometry
        geometry = feature.get("geometry")
        if (geometry):
            id = feature.get("id") or str(f"{type_name}.{index}")
            geom_field_name = feature.get("geometry_name") or self._geometry_name
            field_el = etree.SubElement(feat_el, f"{{{ns}}}{geom_field_name}", {}, {})
            
            # Not : Arcgis'e insert işleminde X/Y bilgilerinin ters olmasından dolayı geometrinin default crs bilgisi (CRS84) yerine
            # Katmanın SRID bilgisi set edilmiştir. Bu sayede encode_v32 işlemi sırasında X/Y bilgilerini kendisi otomatik değiştirmektedir.
            # Ayrıca MultiSurface kısımlarında hata ile karşılaşıldığı için sadece Arcgis tarafında,
            # gelen MultiPolygon tipleri Polygon'a çevrilmiştir. (05.07.2024)
            
            if self._server_type == SpatialServerType.ArcGIS and self._target_proj is not None:
                geometry["crs"] = {"type": "name","properties": {"name": self._target_proj}}
                
                if geometry['type'] == GeometryType.MultiPolygon.value:
                    geometry = self._to_polygon(geometry)
                    
            if self._target_proj != self.DEFAULT_EPSG:
                geometry = self._projection(geometry)   
                
            field_el.append(encode_v32(geometry, id))


    # Not : Gelen MultiPolygon Geometrisini Polygon'a çevirir. (05.07.2024)
    def _to_polygon(self, geometry) -> Any:
        shp = shape(geometry)
        
        if isinstance(shp, MultiPolygon):
            shp = shp.convex_hull
            
        geometry = self._shapely_to_geomdict(shp)    
        return geometry
    
    # Not : Shapely geometrisini pygml da bulunan GeomDict objesine cevirmek için eklenmiştir. (03.07.2024)
    def _shapely_to_geomdict(self, shp) -> GeomDict:
        geom_mapping = mapping(shp)
        geom_dict = GeomDict(
            type=geom_mapping['type'],
            coordinates=geom_mapping['coordinates'],
            crs={"type": "name","properties": {"name": self._target_proj}} # type: ignore
        )
        return geom_dict
    
    
    # Not : Farklı Proj sisteminde geometrik sorguların transform yapılabilmesi için eklenmiştir. (03.07.2024)
    def _projection(self, geometry) -> Any:
        source_proj = self.DEFAULT_EPSG
        shp = shape(geometry)
        
        transformer = Transformer.from_proj(Proj(init=source_proj), Proj(init=self._target_proj))
        projected = transform(transformer.transform, shp)
        
        geometry = self._shapely_to_geomdict(projected)    
        
        return geometry