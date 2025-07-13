import json
import secrets
from datetime import datetime
from collections import OrderedDict
import sys
from dateutil import parser
from typing import Any, Dict, List, Set, Tuple, Union
from sqlalchemy import CHAR, NCHAR, NVARCHAR, TEXT, VARCHAR, Column, ForeignKeyConstraint, MetaData, Table, and_, asc, between, delete, desc, func, insert, nullsfirst, or_, select, update, bindparam, collate
from sqlalchemy.orm import aliased
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterGroup, FilterOp, FilterType, OrderType, QueryArgs
from mapa.core.data.result import ActionResult, PagingResult
from mapa.core.data.util import Util
import re
import elasticapm

class TableDesc:
    """Şema adı ile verilen tablo ismini parçalar, eğer hiyerarşik tablo ise üst alan adını tutar"""

    def __init__(self, full_name: str, parent_col_name: str | None = None) -> None:
        self.full_name = full_name
        self.parent_col_name = parent_col_name
        self.__table_desc = self._split_table_name(full_name)
        self._parent_col_name = parent_col_name

    @property
    def table_name(self):
        """Table name"""
        return self.__table_desc["table"]

    @property
    def schema(self):
        """Schema name"""
        return self.__table_desc["schema"]

    def _split_table_name(self, full_name: str) -> Dict[str, str]:
        parts = full_name.strip().split(".")
        return {
            "schema": "" if len(parts) == 1 else parts[0],
            "table": parts[-1]
        }


class TableRepository:
    """Entity Repository nesneleri için üst sınıf"""
    
    LOCALE_NAME = "tr-TR-x-icu"

    def __init__(self, db: AsyncDatabase, table_desc: TableDesc) -> None:
        self._db = db
        self._table_desc = table_desc
        self.table = self.__create_table_instance(self._table_desc)

    async def count(self, query_args: QueryArgs) -> int:
        """Verilen sorgu parametrelerine göre kayıt sayısını döndürür."""
        count_args = query_args.model_copy()
        count_args.offset = 0
        count_args.limit = sys.maxsize
        count_args.order = None

        alias = self.__generate_alias(self.table)
        field_list, rel_list, join_list = self.__extract_query_args(alias, query_args)

        stmt = None
        if alias._is_table:
            stmt = select(*alias.primary_key).distinct()
        else:
            stmt = select()
            
        if query_args.where:
            stmt = self.__apply_filter(stmt, alias, query_args.where, rel_list)

        async with self._db.session() as session:
            data = await session.execute(select(func.count()).select_from(stmt.subquery()))
            ret_val = data.scalar()

        return ret_val

    def count(self, query_args: QueryArgs) -> int:
        """Verilen sorgu parametrelerine göre modeli sorgular"""
        count_args = query_args.model_copy()

        # Veriyi sınırlandıran offset ve limit değerleri kaldırılır.
        count_args.offset = 0
        count_args.limit = sys.maxsize
        count_args.order = None

        alias = self.__generate_alias(self.table)
        field_list, rel_list, join_list = self.__extract_query_args(
            alias, query_args)

        # Verilerin sadece birincil alanları alınır.
        stmt = None
        if alias._is_table:
            stmt = select(*alias.primary_key).distinct()
        else:
            stmt = select()

        stmt = stmt.select_from(join_list)

        if query_args.where:
            stmt = self.__apply_filter(stmt, alias, query_args.where, rel_list)

        ret_val = 0
        with self._db.session() as session:
            data = session.execute(
                select(func.count()).select_from(stmt.subquery()))
            ret_val = data.scalar()

        return ret_val

    def count_recursive(self, query_args: QueryArgs) -> int:
        # Kök tabloya ait etiket
        alias = self.__generate_alias(self.table)

        # Sorgu parametreleri
        field_list, rel_list, join_list = self.__extract_query_args(
            alias, query_args)

        primary_col_name = alias.primary_key[0].name
        parent_col_name = self._table_desc.parent_col_name

        if not parent_col_name in field_list:
            field_list.append(parent_col_name)

        # Sorgu ifadesi
        fields = self.__create_fields(alias, field_list, rel_list)
        with self._db.session() as session:
            stmt = session.query(*fields)
            stmt = stmt.select_from(join_list)

            # Filtre ifadeleri
            if query_args.where:
                stmt = self.__apply_filter(
                    stmt, alias, query_args.where, rel_list)

            top_query = stmt.cte("cte", recursive=True)
            bottom_query = session.query(*fields).select_from(join_list).join(
                top_query, alias.c[primary_col_name] == top_query.c[parent_col_name])
            recursive_query = top_query.union_all(bottom_query)
            result_query = session.query(recursive_query).distinct().order_by(
                nullsfirst(asc(recursive_query.c[parent_col_name])))

            data = session.execute(
                select(func.count()).select_from(result_query.subquery())
            )
            ret_val = data.scalar()

        return ret_val

    def find_recursive(self, query_args: QueryArgs) -> List[Any]:
        # Kök tabloya ait etiket
        alias = self.__generate_alias(self.table)

        # Sorgu parametreleri
        field_list, rel_list, join_list = self.__extract_query_args(
            alias, query_args)

        primary_col_name = alias.primary_key[0].name
        parent_col_name = self._table_desc.parent_col_name

        if not parent_col_name in field_list:
            field_list.append(parent_col_name)

        # Sorgu ifadesi
        fields = self.__create_fields(alias, field_list, rel_list)
        with self._db.session() as session:
            stmt = session.query(*fields)
            stmt = stmt.select_from(join_list)

            # Filtre ifadeleri
            if query_args.where:
                stmt = self.__apply_filter(
                    stmt, alias, query_args.where, rel_list)

            # Sıralama ifadeleri
            if query_args.order:
                stmt = self.__apply_sort(
                    stmt, alias, query_args.order, rel_list)

            # Limit ve offset değeri
            if query_args.limit:
                stmt = stmt.limit(query_args.limit)

            if query_args.offset:
                stmt = stmt.offset(query_args.offset)

            top_query = stmt.cte("cte", recursive=True)
            bottom_query = session.query(*fields).select_from(join_list).join(
                top_query, alias.c[primary_col_name] == top_query.c[parent_col_name])
            recursive_query = top_query.union_all(bottom_query)
            result_query = session.query(recursive_query).distinct()

            # Sıralama ifadeleri
            if query_args.order:
                orders = OrderedDict(query_args.order)
                for field, order in orders.items():
                    result_query = result_query.order_by(
                        asc(recursive_query.c[field]) if order == "asc" else desc(recursive_query.c[field])
                    )                    

            result = session.execute(result_query)

            data = [dict(row) for row in result.mappings()]

        # Dönüş değeri json modele dönüştürülür
        return [self.__generate_nested_dict(row) for row in data]

    def find(self, query_args: QueryArgs) -> List[Any]:
        """Verilen sorgu parametrelerine göre modeli sorgular"""

        # Kök tabloya ait etiket
        alias = self.__generate_alias(self.table)

        # Sorgu parametreleri
        field_list, rel_list, join_list = self.__extract_query_args(
            alias, query_args)

        # Sorgu ifadesi
        fields = self.__create_fields(alias, field_list, rel_list)
        stmt = select(*fields)
        stmt = stmt.select_from(join_list)

        # Filtre ifadeleri
        if query_args.where:
            stmt = self.__apply_filter(stmt, alias, query_args.where, rel_list)

        # Sıralama ifadeleri
        if query_args.order:
            stmt = self.__apply_sort(stmt, alias, query_args.order, rel_list)

        # Limit ve offset değeri
        if query_args.limit:
            stmt = stmt.limit(query_args.limit)

        if query_args.offset:
            stmt = stmt.offset(query_args.offset)

        _, data = self.__execute_statement(stmt, {})

        # Dönüş değeri json modele dönüştürülür
        return [self.__generate_nested_dict(row) for row in data]

    def paging(self, query_args: QueryArgs) -> PagingResult[Any]:
        """Verilen sorgu parametrelerine göre PagingResult döndürür"""

        ret_val = PagingResult(
            total=0, items=[], offset=query_args.offset, limit=query_args.limit)

        if self._table_desc.parent_col_name:
            # Eğer bir filtre yoksa hiyerarşinin en üstündekiler getirilir
            if query_args.where is None or len(query_args.where) == 0:
                query_args.where = [
                    Filter(field=self._table_desc.parent_col_name,
                           op=FilterOp.NULL)
                ]
            ret_val.total = self.count_recursive(query_args)
            if ret_val.total > 0:
                ret_val.items = self.find_recursive(query_args)
        else:
            ret_val.total = self.count(query_args)
            if ret_val.total > 0:
                ret_val.items = self.find(query_args)
        return ret_val

    def create(self, data: List[Dict[str, Any]] | Dict[str, Any]) -> ActionResult[Any]:
        """Yeni bir kayıt oluşturur"""

        values = data if isinstance(data, List) else [data]

        # Oluşturma zamanı eklenir
        if any(c.name == "created_at" for c in self.table.columns):
            values = list(
                map(lambda x: {**x, "created_at": datetime.now()}, values))

        if self._table_desc.parent_col_name:
            for val in values:
                val[self._table_desc.parent_col_name] = val.get(
                    self._table_desc.parent_col_name)

        # Verinin kolonları tabloya uyarlanır.
        values = self.__flatten_values(values)

        # Eksik parametreler tamamlanır. Boş olan parametreler yerine None değeri eklenir.
        values = self.__add_missing_properties(values)

        stmt = insert(self.table).values(
            values).returning(self.table)

        if self._db.engine.dialect.use_insertmanyvalues == False:
            affected, items = self.__execute_insert_single(self.table, values)
        else:
            affected, items = self.__execute_statement(stmt, None)

        return ActionResult(
            success=True,
            affected=affected,
            items=items
        )

    def update(self, data: List[Dict[str, Any]] | Dict[str, Any]) -> ActionResult[Any]:
        """QueryArg verilen kaydı günceller"""

        values = data if isinstance(data, List) else [data]

        # Günceleme zamanı eklenir
        if any(c.name == "updated_at" for c in self.table.columns):
            values = list(
                map(lambda x: {**x, "updated_at": datetime.now()}, values))

        # Verinin kolonları tabloya uyarlanır.
        values = self.__flatten_values(values)

        # Eksik parametreler tamamlanır. Boş olan parametreler yerine None değeri eklenir.
        values = self.__add_missing_properties(values)

        stmt = update(self.table)

        for pkey_col in self.table.primary_key.columns:
            stmt = stmt.where(pkey_col == bindparam("b_id"))

        # id alanı bindparam da reserve olduğu için id değiştirilir.
        new_values = []
        for value in values:
            if value.get("id") is not None:
                value["b_id"] = value.pop("id")
            new_values.append(value)

        # Sorgu şablonu hazırlanır.
        value = new_values[0]
        template = {key: bindparam(key) for key in value.keys()}

        stmt.values(template)

        affected, items = self.__execute_statement(stmt, values)

        return ActionResult(
            success=True,
            affected=affected,
            items=items
        )

    def update_with_query(self, query_args: QueryArgs, data: Dict[str, Any]) -> ActionResult[Any]:
        """QueryArg verilen kaydı günceller"""
        if not query_args.where:
            raise ValueError("QueryArgs without where clause")

        # Günceleme zamanı eklenir
        if any(c.name == "updated_at" for c in self.table.columns):
            data["updated_at"] = datetime.now()

        # Verinin kolonları tabloya uyarlanır.
        data = self.__flatten_values([data])[0]

        # Kök tabloya ait etiket
        alias = self.__generate_alias(self.table)

        # Sorgu parametreleri
        field_list, rel_list, join_list = self.__extract_query_args(
            alias, query_args)

       # Select ifadesi
        select_stmt = select(alias.primary_key[0])
        select_stmt = select_stmt.select_from(join_list)
        if query_args.where:
            select_stmt = self.__apply_filter(
                select_stmt, alias, query_args.where, rel_list)

        # Update ifadesi
        update_stmt = update(self.table).\
            where(self.table.primary_key.columns[0].in_(select_stmt.scalar_subquery())).\
            values(data)

        affected, items = self.__execute_statement(update_stmt, None)

        return ActionResult(
            success=True,
            affected=affected,
            items=items
        )

    def delete(self, query_args: QueryArgs) -> ActionResult[Any]:
        """QueryArg verilen kaydı günceller"""
        if not query_args.where:
            raise ValueError("QueryArgs without where clause")

        # Kök tabloya ait etiket
        alias = self.__generate_alias(self.table)

        # Sorgu parametreleri
        field_list, rel_list, join_list = self.__extract_query_args(
            alias, query_args)

       # Select ifadesi
        select_stmt = select(alias.primary_key[0])
        select_stmt = select_stmt.select_from(join_list)
        if query_args.where:
            select_stmt = self.__apply_filter(
                select_stmt, alias, query_args.where, rel_list)

        # Delete ifadesi
        delete_stmt = delete(self.table).\
            where(self.table.primary_key.columns[0].in_(
                select_stmt.scalar_subquery()))

        affected, items = self.__execute_statement(delete_stmt, None)

        return ActionResult(
            success=True,
            affected=affected,
            items=items
        )

    def __create_field_list(self, query_args: QueryArgs) -> List[str]:
        """QueryArgs içindeki filter, select ve sort parametrelerinden alan listesi oluşturur."""

        def extract_fields(field_list: List[str], filter_list: List[Union[Filter, FilterGroup]]):
            for filterx in filter_list:
                if filterx.type == "filter":
                    if filterx.field not in field_list:
                        field_list.append(filterx.field)
                else:
                    extract_fields(field_list, filterx.filters)

        # Dönüş listesi
        return_val = []

        # Model verildiyse alanlar modelden oluşturularak select listesine set edilir.
        if query_args.model:
            model_fields = []
            self.__extract_fields_from_model(
                model_fields, query_args.model, None)
            query_args.select = model_fields

        # select parametreleri eklenir
        if query_args.select:
            return_val.extend([
                x for x in query_args.select if x not in return_val
            ])

        # # filter alanları eklenir
        # if query_args.where:
        #     extract_fields(return_val, query_args.where)

        # Sort parametreleri eklenir
        # if query_args.order:
        #     return_val.extend([
        #         key for key in query_args.order if key not in return_val
        #     ])

        # Alanlar sıralanır. referans alanları ile diğer alanlar
        # ayrı ayrı sıralanıp toplanır.
        lst_without_dot = []
        lst_with_dot = []

        for item in return_val:
            if '.' in item:
                lst_with_dot.append(item)
            else:
                lst_without_dot.append(item)

        lst_without_dot.sort()
        lst_with_dot.sort()

        return lst_without_dot + lst_with_dot

    def __create_expand_list(self, field_list: List) -> List[str]:
        """Alan listesindeki değerlere göre bir expand (join table) listesi oluşturur.
        Alan listesi select, filter ya da sort bölümlerinden gelen iç içe alanlar olabilir.
        iç içe alanlar kullanılarak bir expand listesi oluşturulur. 
        Örneğin Kisi tablosunda
            "id", "ad", "soyad",
            "ev_adres_id", "ev_adres_id.id", "ev_adres_id.kapi_no",
            "is_adres_id", "is_adres_id.id", "is_adres_id.kapi_no",
            "ilce_id", "ilce_id.id", "ilce_id.ad"

        Bu durumda oluşacak expand listesi ["ev_adres_id","is_adres_id", "ilce_id] olacaktır.
        Args:
            field_list (List): Alan listesi
        """
        expand_list = []
        for field in field_list:
            if "." in field:
                expand = ".".join(field.split(".")[:-1])
                if expand not in expand_list:
                    expand_list.append(expand)

        return expand_list

    def __create_table_instance(self, table_desc: TableDesc) -> Table:
        table_name = table_desc.table_name
        schema = table_desc.schema
        metadata = MetaData()
        table = Table(table_name, metadata, schema=schema,
                      autoload_with=self._db.engine)
        # self._inspector.reflect_table(table, None)
        return table

    def __apply_relations(self, start_alias: Any, join_grps: Any) -> Any:
        """expand listesindeki property listesini join olarak modele ekler"""
        # Joinler eklenir
        joined = start_alias
        for _, join_grp in join_grps.items():
            # Joinler oluşturulur.
            from_alias = join_grp["from_alias"]
            to_alias = join_grp["to_alias"]
            from_col = join_grp['from_column']
            to_col = join_grp['to_column']
            joined = joined.outerjoin(
                to_alias, from_alias.c[from_col] == to_alias.c[to_col])
        return joined

    def __find_relations(self, start_alias: Any, expand: List[str]) -> OrderedDict[str, Any]:
        """expand listesindeki alanlara ait tabloları bulur """

        join_grps = OrderedDict()
        for rel in expand:
            field_names = rel.split(".")
            from_alias = start_alias
            for field_name in field_names:
                fk_constraint = self.__find_fk_contraint(
                    from_alias.element, field_name)
                if fk_constraint is None:
                    raise ValueError(field_name + " fk contstaint not found")
                to_alias = self.__generate_alias(fk_constraint.referred_table)
                key = join_grps.get(field_name)
                if not key:
                    key = {
                        "path": rel,
                        "field": field_name,
                        "from_alias": from_alias,
                        "to_alias": to_alias,
                        "from_column": fk_constraint.columns[0].name,
                        "to_column": fk_constraint.elements[0].column.name
                    }
                    join_grps[field_name] = key
                from_alias = key["to_alias"]
        return join_grps

    def __generate_alias(self, table: Table, size: int = 8) -> Any:
        alphabet = "qwertyuopilkjhgfdsazxcvbnm"
        alias_name = ''.join(secrets.choice(alphabet) for i in range(size))
        return aliased(table, name=alias_name)

    def __apply_filter(self, stmt, root_alias: Any, filters: List[Union[Filter, FilterGroup]], join_grps: Any = None) -> Any:
        """Filtreleri sorgu cümlesine ekler. Filtreler hiyerarşik modelde olabilir
        filter(and(a_filter, b_filter, or(c_filter, d_filter)), e_filter)
        """

        def apply_filter(filter_list: List,  filtery: Filter | FilterGroup, join_grps):
            if filtery.type == "filter":
                parts = filtery.field.split(".")
                field_name = parts[-1]
                filter_attr = None
                if len(parts) == 1:
                    filter_attr = root_alias.c[field_name]
                else:
                    path = ".".join(parts[:-1])
                    join_grp = next(
                        filter(lambda x: x[1]["path"] == path, join_grps.items()))
                    to_alias = join_grp[1]["to_alias"]
                    if to_alias is not None:
                        filter_attr = to_alias.c[field_name]
                    else:
                        raise ValueError(filtery)
                if filter_attr is None:
                    raise ValueError(f"{filtery.field} field not found")

                # Filtreler uygulanır
                cast_value = filtery.value if filtery.value is None else self.__cast_field_value(
                    filter_attr, filtery.value)  # type: ignore
                match filtery.op:
                    case FilterOp.EQUAL:
                        filter_list.append(filter_attr.__eq__(cast_value))
                    case FilterOp.NOT_EQUAL:
                        filter_list.append(filter_attr.__ne__(cast_value))
                    case FilterOp.NULL:
                        filter_list.append(filter_attr.is_(None))
                    case FilterOp.NOT_NULL:
                        filter_list.append(filter_attr.is_not(None))
                    case FilterOp.IN:
                        filter_list.append(filter_attr.in_(cast_value))
                    case FilterOp.NOT_IN:
                        filter_list.append(filter_attr.not_in(cast_value))
                    case FilterOp.LESS_THAN:
                        filter_list.append(filter_attr.__lt__(cast_value))
                    case FilterOp.LESS_THAN_OR_EQUAL:
                        filter_list.append(filter_attr.__le__(cast_value))
                    case FilterOp.LIKE:
                        filter_list.append(filter_attr.like(cast_value))
                    case FilterOp.ILIKE:
                        filter_list.append(filter_attr.ilike(cast_value))
                    case FilterOp.NOT_LIKE:
                        filter_list.append(filter_attr.not_like(cast_value))
                    case FilterOp.NOT_ILIKE:
                        filter_list.append(
                            filter_attr.not_ilike(cast_value))
                    case FilterOp.MORE_THAN:
                        filter_list.append(filter_attr.__gt__(cast_value))
                    case FilterOp.MORE_THAN_OR_EQUAL:
                        filter_list.append(filter_attr.__ge__(cast_value))
                    case FilterOp.BETWEEN:
                        lower = cast_value[0]
                        upper = cast_value[1]
                        filter_list.append(between(filter_attr, lower, upper))
            else:
                sub_filter_list = []
                for filterz in filtery.filters:
                    apply_filter(sub_filter_list, filterz, join_grps)
                if filtery.type == FilterType.AND:
                    filter_list.append(and_(*sub_filter_list))
                else:
                    filter_list.append(or_(*sub_filter_list))

        filter_list = []
        for filterx in filters:
            apply_filter(filter_list, filterx, join_grps)

        if len(filter_list) > 0:
            stmt = stmt.filter(*filter_list)

        return stmt

    # Not : parser.isoparse methodunda sadece aşağıdaki formatlar destekleniyormuş.
    # Second Party üzerinde de artık format verildiği için hataya neden oluyordu.
    # 16.05.2024
    # YYYY
    # YYYY-MM
    # YYYY-MM-DD or YYYYMMDD
    def __cast_field_value(self, filter_attr: Any, value: Any) -> Any:
        def is_iso_datetime(s: str):
            try:
                # length parametresi tarih için 8 karakterden fazla olması şartında parse edilmesi için eklendi.
                # aksi halde '21' stringini 21.xx.xxxx'e çeviriyordu. 
                # 16.05.2024
                if len(s) >= 8:
                    if re.match(Util.DDMMYYYHHmmssPattern, s) or re.match(Util.DDMMYYYPattern, s) or re.match(Util.DDMMYYYHHmmssSlashPattern, s)or re.match(Util.DDMMYYYSlashPattern, s):
                        return parser.parse(s, dayfirst=True).replace(tzinfo=None)
                    elif re.match(Util.dateIsoPattern, s):
                        return parser.isoparse(s).replace(tzinfo=None)
                    else:
                        return parser.parse(s).replace(tzinfo=None)
            except Exception:
                return None

        def create_value_object(value_type, val) -> Any:
            ret_obj = is_iso_datetime(val)
            if ret_obj is None:
                ret_obj = val if type(
                    val) == value_type else value_type(str(val))
            return ret_obj

        ret_val = value
        value_type = filter_attr.type.python_type
        # if type(value) == list:
        #     ret_val = [create_value_object(value_type, item) for item in value]
        # else:
        #     ret_val = value if type(
        #         value) == value_type else create_value_object(value_type, value)
            
        if isinstance(value, list):
            ret_val = [
                item if isinstance(item, value_type) else create_value_object(value_type, item)
                for item in value
            ]
        else:
            ret_val = value if isinstance(value, value_type) else create_value_object(value_type, value)
            
        return ret_val

    def __apply_sort(self, stmt, root_alias: Any, sort: Dict[str, OrderType], join_grps: Any) -> Any:
        """Sorguya sıralama kriterlerini ekler"""

        order_list = []
        for field_expr in sort:
            direction = sort[field_expr]
            parts = field_expr.split(".")
            field_name = parts[-1]
            filter_attr = None
            if len(parts) == 1:
                filter_attr = root_alias.c[field_name]
            else:
                path = ".".join(parts[:-1])
                join_grp = next(
                    filter(lambda x: x[1]["path"] == path, join_grps.items()))
                to_alias = join_grp[1]["to_alias"]
                if to_alias is not None:
                    filter_attr = to_alias.c[field_name]
                else:
                    raise ValueError(field_expr)
            if filter_attr is None:
                raise ValueError(f"{field_expr} field not found")

            # Text ya da Char alanlara locale eklenir
            filter_attr = self.__set_locale(filter_attr, self.LOCALE_NAME)
            order_list.append(
                filter_attr.desc() if direction.lower() == "desc" else filter_attr.asc()
            )

        if len(order_list) > 0:
            stmt = stmt.order_by(*order_list)

        return stmt

    def __extract_fields_from_model(self, field_list: List[str], item: List[Any], parent_key: str | None):
        """Model olarak gelen alan listesini nokta formasyona çevirir. 
        ["id", "name", "sub_field": ["id", "name"]] => ["id", "name", "sub_field.id", "sub_field.name]
        """
        for sub_item in item:
            if isinstance(sub_item, dict):
                for k, v in sub_item.items():
                    self.__extract_fields_from_model(
                        field_list, v, parent_key + "." + k if parent_key else k)
            else:
                field_list.append(parent_key + "." +
                                  sub_item if parent_key else sub_item)

    def __extract_query_args(self, alias: Any, query_args: QueryArgs) -> Tuple[Any, Any, Any]:  
        if query_args:
            try:
                encoded_params = json.dumps(query_args.to_serialize(), ensure_ascii=False, cls=JsonEncoder)
                elasticapm.set_custom_context({  # type: ignore
                    "query_params": encoded_params
                })
            except Exception as ex:
                elasticapm.set_custom_context({  # type: ignore
                    "query_params": str(query_args),
                    "query_params_parse_error": str(ex)
                })
                
        field_list = self.__create_field_list(query_args)
        if len(field_list) == 0:
            field_list = [field.name for field in alias.c]
        expand_list = self.__create_expand_list(field_list)
        rel_list = self.__find_relations(alias, expand_list)
        join_list = self.__apply_relations(alias, rel_list)

        return (field_list, rel_list, join_list)

    def __create_fields(self, root_alias: Any, field_list: List[str], rels: OrderedDict[str, Any]):
        fields = []
        for field in field_list:
            parts = field.split(".")
            if len(parts) > 1:
                path = ".".join(parts[:-1])
                join_grp = next(
                    filter(lambda x: x[1]["path"] == path, rels.items()))
                alias = join_grp[1]["to_alias"]
            else:
                alias = root_alias
            fields.append(alias.c[parts[-1]].label(field))

        return fields

    def __execute_statement(self, stmt: Any, params: Any, options: Any = None) -> Tuple[int, Any]:        
        if params:
            try:
                encoded_params = json.dumps(params, ensure_ascii=False, cls=JsonEncoder)
                elasticapm.set_custom_context({  # type: ignore
                    "params": encoded_params
                })
            except Exception as ex:
                elasticapm.set_custom_context({  # type: ignore
                    "params": str(params),
                    "param_parse_error": str(ex)
                })
            
        with self._db.session() as session:
            result = session.execute(
                stmt, params, execution_options=options or {})
            data = [dict(row) for row in result.mappings()
                    ] if result.returns_rows else []
            row_count = result.rowcount
            session.commit()
        return (row_count, data)

    def __execute_insert_single(self, table: Table, valuesList: List[Any], options: Any = None) -> Tuple[int, Any]:
        if valuesList:
            try:
                elasticapm.set_custom_context({  # type: ignore
                    "insert_values": json.loads(json.dumps(valuesList, ensure_ascii=False, cls=JsonEncoder))
                })
            except Exception as ex:
                elasticapm.set_custom_context({  # type: ignore
                    "insert_values": str(valuesList),
                    "param_parse_error": str(ex)
                })
                
        stmt = insert(table)
        with self._db.session() as session:
            row_count = 0
            data_list = []
            for values in valuesList:
                stmt2 = stmt.values(values).returning(table)
                result = session.execute(
                    stmt2, None, execution_options=options or {})
                data = [dict(row) for row in result.mappings()
                        ] if result.returns_rows else []
                row_count += 1
                data_list.append(data)
            session.commit()
        return (row_count, data_list)

    def __generate_nested_dict(self, row: Dict[str, Any]):
        result = {}
        for key, value in row.items():
            if '.' in key:
                nested_keys = key.split('.')
                current_dict = result
                for nested_key in nested_keys[:-1]:
                    current_dict.setdefault(nested_key, {})
                    temp_dict = current_dict[nested_key]
                    if not isinstance(temp_dict, Dict):
                        current_dict[nested_key] = {}
                        current_dict = current_dict[nested_key]
                    else:
                        current_dict = temp_dict
                current_dict[nested_keys[-1]] = value
            else:
                result[key] = value
        return result

    def __get_parent_column(self, table: Table, parent_column: str) -> Tuple[str, Column | None]:
        foreign_keys: Set[ForeignKeyConstraint] = table.foreign_key_constraints
        fk_list = list(
            filter(lambda x: x.referred_table == table, foreign_keys))
        fk_count = len(fk_list)
        # Eğer bir kendine referanslı alan varsa o döndürülür, isme bakılmaz
        if fk_count == 1:
            return fk_list[0].columns.items()[0]
        elif fk_count > 1:
            # Birden çok kendine referanslı alan varsa parent_colum alanı kullanılır
            if parent_column:
                foreign_key = next(
                    filter(lambda x: x.columns[0].name == parent_column, fk_list), None)
                if foreign_key is not None:
                    return foreign_key.columns.items()[0]
                else:
                    return ("", None)
            else:
                return fk_list[0].columns.items()[0]

        return ("", None)

    def __find_fk_contraint(self, table: Table, col_name: str) -> ForeignKeyConstraint | None:
        fk_list = table.foreign_key_constraints
        fk_constraint = next(
            filter(lambda x: x.column_keys[0] == col_name, fk_list), None)
        return fk_constraint

    def __flatten_values(self, data: List[Any]) -> List[Any]:
        new_list = []
        for row in data:
            new_row = dict()
            for key, item in row.items():
                # İstekte gönderilen alanların tabloda bulunması gerekir.
                col = next(filter(lambda x: x.name ==
                           key, self.table.columns), None)
                if not col is None:
                    if isinstance(item, Dict):
                        fk_contraint = self.__find_fk_contraint(
                            self.table, key)
                        if fk_contraint is not None:
                            fk_col_name = fk_contraint.referred_table.primary_key.columns[0].name
                            value = item.get(fk_col_name)
                            if not value is None:
                                new_row[key] = value
                    else:
                        new_row[key] = item
            new_list.append(new_row)

        return new_list

    def __add_missing_properties(self, list_of_dicts: List[Dict[Any, Any]]):
        # Find all unique property names across all dictionaries
        all_properties = set()
        for item in list_of_dicts:
            all_properties.update(item.keys())

        # Iterate through each dictionary and add missing properties with None value
        for item in list_of_dicts:
            missing_properties = all_properties.difference(item.keys())
            for prop in missing_properties:
                item[prop] = None

        return list_of_dicts        
        
        
    def __set_locale(self, filter_attr: Any, locale_name: str) -> Any:
        if isinstance(filter_attr.type, VARCHAR) or \
            isinstance(filter_attr.type, NVARCHAR) or \
            isinstance(filter_attr.type, TEXT) or \
            isinstance(filter_attr.type, CHAR) or \
            isinstance(filter_attr.type, NCHAR):
            filter_attr = filter_attr.collate(locale_name)
        return filter_attr