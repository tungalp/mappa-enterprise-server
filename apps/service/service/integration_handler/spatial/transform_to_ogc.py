from typing import Any
from uuid import uuid4
from mapa.core.data.query_args import Filter, FilterGroup, FilterOp, FilterType, QueryArgs
from owslib.fes2 import BBox,And, Or, Not, PropertyIsEqualTo, \
    PropertyIsBetween, PropertyIsGreaterThan, PropertyIsGreaterThanOrEqualTo, PropertyIsLessThan, \
    PropertyIsLessThanOrEqualTo, PropertyIsLike, PropertyIsNotEqualTo,PropertyIsNull, \
    Intersects, Contains, Disjoint, Within, Touches, Overlaps, Equals  
from lxml import etree
from pygml.v32 import encode_v32, GeomDict
from pyproj import Transformer,Proj
from shapely.ops import transform
from shapely.geometry import shape, mapping


class XGeometry:
    def __init__(self, geom) -> None:
        self.geom = geom

    def toXML(self):
        return self.geom

class TransformToOGC:
    """QueryArgs filtrelerini CQL_FILTER filtrelerine dönüştürür"""
    
    # Define the namespaces
    DEFAULT_NS_MAP = {
        "wfs": "http://www.opengis.net/wfs",
        "gml": "http://www.opengis.net/gml",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "fes": "http://www.opengis.net/fes/2.0"
    }
    
    DEFAULT_EPSG =  "EPSG:4326"
    
    def transform(self, query_args: QueryArgs, target_proj = "EPSG:4326") -> Any:
        """QueryArgs nesnesini OGC Filter Encoding yapısına dönüştürür"""

        root = etree.Element("{%s}Filter" % self.DEFAULT_NS_MAP["fes"], {}, {})
        filters = []
        if query_args.where:
            for filter_expr in query_args.where:
                if filter_expr.type == FilterType.FILTER:
                    filter_el = self._transform_filter(filter_expr, target_proj)  # type: ignore
                    filters.append(filter_el)
                else:
                    group_el = self._transform_filter_group(filter_expr, target_proj)  # type: ignore
                    filters.append(group_el)
        if len(filters) > 1:
            root.append(And(filters).toXML())
        elif len(filters) == 1:
            root.append(filters[0].toXML())

        return root
    
    def _transform_filter(self, filterx: Filter, target_proj: str) -> Any:
        ogc_filter = None
        match filterx.op:
            case FilterOp.EQUAL:
                ogc_filter = PropertyIsEqualTo(filterx.field, str(filterx.value))
            case FilterOp.NOT_EQUAL:
                ogc_filter = PropertyIsNotEqualTo(filterx.field, str(filterx.value))
            case FilterOp.NULL:
                ogc_filter = PropertyIsNull(filterx.field)
            case FilterOp.NOT_NULL:
                ogc_filter = Not([PropertyIsNull(filterx.field)])
            case FilterOp.IN:
                ogc_filter = Or([PropertyIsEqualTo(filterx.field, str(item)) for item in filterx.value]) # type: ignore
            case FilterOp.NOT_IN:
                ogc_filter = And([PropertyIsNotEqualTo(filterx.field, str(item)) for item in filterx.value]) # type: ignore
            case FilterOp.LESS_THAN:
                ogc_filter = PropertyIsLessThan(filterx.field, str(filterx.value))
            case FilterOp.LESS_THAN_OR_EQUAL:
                ogc_filter = PropertyIsLessThanOrEqualTo(filterx.field, str(filterx.value))
            case FilterOp.LIKE:
                ogc_filter = PropertyIsLike(filterx.field, str(filterx.value))
            case FilterOp.ILIKE:
                ogc_filter = PropertyIsLike(filterx.field, str(filterx.value))
            case FilterOp.NOT_LIKE:
                ogc_filter = Not([PropertyIsLike(filterx.field, str(filterx.value))])
            case FilterOp.NOT_ILIKE:
                ogc_filter = Not([PropertyIsLike(filterx.field, str(filterx.value))])
            case FilterOp.MORE_THAN:
                ogc_filter = PropertyIsGreaterThan(filterx.field, str(filterx.value))
            case FilterOp.MORE_THAN_OR_EQUAL:
                ogc_filter = PropertyIsGreaterThanOrEqualTo(filterx.field, str(filterx.value))
            case FilterOp.BETWEEN:
                lower = (str(filterx.value) or [""])[0]
                upper = (str(filterx.value) or ["", ""])[1]
                ogc_filter = PropertyIsBetween(filterx.field, lower, upper)
            case FilterOp.BBOX:
                ogc_filter = BBox(filterx.value)
            case FilterOp.EQUALS:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                shp = self._shapely_to_geomdict(shp, target_proj)    
                geom = encode_v32(shp, str(uuid4())) # type: ignore
                ogc_filter = Equals(filterx.field, XGeometry(geom))
            case FilterOp.DISJOINT:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                shp = self._shapely_to_geomdict(shp, target_proj)    
                geom = encode_v32(shp, str(uuid4())) # type: ignore
                ogc_filter = Disjoint(filterx.field, XGeometry(geom))
            case FilterOp.INTERSECTS:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                shp = self._shapely_to_geomdict(shp, target_proj)    
                geom = encode_v32(shp, str(uuid4())) # type: ignore
                ogc_filter = Intersects(filterx.field, XGeometry(geom))
            case FilterOp.TOUCHES:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                shp = self._shapely_to_geomdict(shp, target_proj)    
                geom = encode_v32(shp, str(uuid4())) # type: ignore
                ogc_filter = Touches(filterx.field, XGeometry(geom))
            # case FilterOp.CROSSES:

            case FilterOp.WITHIN:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                shp = self._shapely_to_geomdict(shp, target_proj)    
                geom = encode_v32(shp, str(uuid4())) # type: ignore
                ogc_filter = Within(filterx.field, XGeometry(geom))
            case FilterOp.CONTAINS:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                shp = self._shapely_to_geomdict(shp, target_proj)    
                geom = encode_v32(shp, str(uuid4())) # type: ignore
                ogc_filter = Contains(filterx.field, XGeometry(geom))
            case FilterOp.OVERLAPS:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                shp = self._shapely_to_geomdict(shp, target_proj)    
                geom = encode_v32(shp, str(uuid4())) # type: ignore
                ogc_filter = Overlaps(filterx.field, XGeometry(geom))

        return ogc_filter


    def _transform_filter_group(self, filter_group: FilterGroup, target_proj: str) -> Any:
        filters = []
        for filter_expr in filter_group.filters:
            if filter_expr.type == FilterType.FILTER:
                filter_el = self._transform_filter(filter_expr, target_proj)  # type: ignore
                if filter_el:
                    filters.append(filter_el)
            else:
                group_el = self._transform_filter_group(filter_expr, target_proj)  # type: ignore
                filters.append(group_el)

        return And(filters) if filter_group.type == FilterType.AND else Or(filters)

    # Farklı Proj sisteminde geometrik sorguların transform yapılabilmesi için eklenmiştir. (03.07.2024)
    def _projection(self, shape, proj) -> Any:
        source_proj = self.DEFAULT_EPSG
        target_proj = proj
        
        transformer = Transformer.from_proj(Proj(init=source_proj), Proj(init=target_proj))
        projected = transform(transformer.transform, shape)
        return projected
    
    # Shapely geometrisini pygml da bulunan GeomDict objesine cevirmek için eklenmiştir. (03.07.2024)
    def _shapely_to_geomdict(self, geom, target_proj) -> GeomDict:
        geom_mapping = mapping(geom)
        geom_dict = GeomDict(
            type=geom_mapping['type'],
            coordinates=geom_mapping['coordinates'],
            crs={"type": "name","properties": {"name": target_proj}} # type: ignore
        )
        return geom_dict