from typing import Any
from mapa.core.data.query_args import Filter, FilterGroup, FilterOp, FilterType, QueryArgs
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer,Proj

class TransformToCQL:
    """QueryArgs filtrelerini CQL_FILTER filtrelerine dönüştürür"""
    
    
    DEFAULT_EPSG =  "EPSG:4326"
    
    def transform(self, query_args: QueryArgs, target_proj = "EPSG:4326") -> str:
        filters = []
        if (query_args.where):
            for filter_expr in query_args.where:
                if filter_expr.type == FilterType.FILTER:
                    filter_str = self._transform_filter(filter_expr, target_proj)  # type: ignore
                    filters.append(filter_str)
                else:
                    group_str = self._transform_filter_group(filter_expr, target_proj)  # type: ignore
                    filters.append(f"({group_str})")
        return " and ".join(filters)
    
    def _transform_filter(self, filterx: Filter, target_proj: str) -> str:
        filter_str = ""
        match filterx.op:
            case FilterOp.EQUAL:
                filter_str = f"{filterx.field}{' = '}'{filterx.value}'"
            case FilterOp.NOT_EQUAL:
                filter_str = f"{filterx.field}{' <> '}'{filterx.value}'"
            case FilterOp.NULL:
                filter_str = f"{filterx.field}{' IS NULL'}"
            case FilterOp.NOT_NULL:
                filter_str = f"{filterx.field}{' IS NOT NULL'}"
            case FilterOp.IN:
                filter_str = f"{filterx.field}{' IN '} ({','.join(str(item) for item in filterx.value)})" # type: ignore
            case FilterOp.NOT_IN:
                filter_str = f"{filterx.field}{' NOT IN '} ({','.join(str(item) for item in filterx.value)})" # type: ignore
            case FilterOp.LESS_THAN:
                filter_str = f"{filterx.field}{' < '}'{filterx.value}'"
            case FilterOp.LESS_THAN_OR_EQUAL:
                filter_str = f"{filterx.field}{' <= '}'{filterx.value}'"
            case FilterOp.LIKE:
                filter_str = f"{filterx.field}{' LIKE '}'{filterx.value}'"
            case FilterOp.ILIKE:
                filter_str = f"{filterx.field}{' ILIKE '}'{filterx.value}'"
            case FilterOp.NOT_LIKE:
                filter_str = f"{filterx.field}{' NOT LIKE '}'{filterx.value}'"
            case FilterOp.NOT_ILIKE:
                filter_str = f"{filterx.field}{' NOT ILIKE '}'{filterx.value}'"
            case FilterOp.MORE_THAN:
                filter_str = f"{filterx.field}{' > '}'{filterx.value}'"
            case FilterOp.MORE_THAN_OR_EQUAL:
                filter_str = f"{filterx.field}{' >= '}'{filterx.value}'"
            case FilterOp.BETWEEN:
                lower = (filterx.value or [""])[0]
                upper = (filterx.value or ["", ""])[1]
                filter_str = f"{filterx.field}{' BETWEEN '}{lower} { ' AND '}{upper}"
            # Spatial Filters
            case FilterOp.BBOX:
                filter_str = f"BBOX({filterx.field},{','.join([str(coord) for coord in filterx.value or []])})"
            case FilterOp.EQUALS:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"EQUALS({filterx.field},{shp.wkt})"  
            case FilterOp.DISJOINT:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"DISJOINT({filterx.field},{shp.wkt})"  
            case FilterOp.INTERSECTS:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"INTERSECTS({filterx.field},{shp.wkt})"    
            case FilterOp.TOUCHES:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"TOUCHES({filterx.field},{shp.wkt})"  
            case FilterOp.CROSSES:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"CROSSES({filterx.field},{shp.wkt})"  
            case FilterOp.WITHIN:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"WITHIN({filterx.field},{shp.wkt})"  
            case FilterOp.CONTAINS:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"CONTAINS({filterx.field},{shp.wkt})"  
            case FilterOp.OVERLAPS:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"OVERLAPS({filterx.field},{shp.wkt})"  
            case FilterOp.RELATE:
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"RELATE({filterx.field},{shp.wkt})"  
            # Distance Operators
            case FilterOp.DWITHIN:
                distance = dict(filterx.value or {}).get("distance") or 0.0
                unit = dict(filterx.value or {}).get("unit") or "meters"
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"DWITHIN({filterx.field},{shp.wkt},{distance},{unit})"  
            case FilterOp.BEYOND:
                distance = dict(filterx.value or {}).get("distance") or 0.0
                unit = dict(filterx.value or {}).get("unit") or "meters"
                shp = shape(filterx.value)
                if target_proj != self.DEFAULT_EPSG:    
                    shp = self._projection(shp, target_proj)
                filter_str = f"BEYOND({filterx.field},{shp.wkt},{distance},{unit})"  

        return filter_str


    def _transform_filter_group(self, filter_group: FilterGroup, target_proj: str) -> str:
        filters = []
        for filter_expr in filter_group.filters:
            if filter_expr.type == FilterType.FILTER:
                filter_str = self._transform_filter(filter_expr, target_proj)  # type: ignore
                filters.append(filter_str)
            else:
                group_str = self._transform_filter_group(filter_expr, target_proj)  # type: ignore
                filters.append(group_str)
        return str(f" {filter_group.type.value} ").join(filters)

    # Farklı Proj sisteminde geometrik sorguların transform yapılabilmesi için eklenmiştir. (18.04.2024)
    def _projection(self, shape, proj) -> Any:
        source_proj =  self.DEFAULT_EPSG
        target_proj = proj
        
        transformer = Transformer.from_proj(Proj(init=source_proj), Proj(init=target_proj))
        projected = transform(transformer.transform, shape)
        return projected