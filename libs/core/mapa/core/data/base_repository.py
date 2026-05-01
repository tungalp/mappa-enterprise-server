import sys
import re
from dateutil import parser
from abc import ABC
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, Generic, List, Type, TypeVar, Union
from sqlalchemy.orm import contains_eager
from sqlalchemy.inspection import inspect
from sqlalchemy import  Text, CHAR, NCHAR, NVARCHAR, TEXT, VARCHAR, and_, or_, between, select, delete, text, update as update_db, func
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity import Base
from mapa.core.data.query_args import Filter, FilterGroup, FilterOp, FilterType, QueryArgs
from mapa.core.data.util import Util
from sqlalchemy import CHAR, NCHAR, NVARCHAR, TEXT, VARCHAR, and_, asc, between, delete, desc, func, insert, nullsfirst, or_, select, update, bindparam, collate


EntityType = TypeVar("EntityType", bound=Base)


class BaseRepository(ABC, Generic[EntityType]):
    """Entity Repository nesneleri için üst sınıf"""

    LOCALE_NAME = "tr-TR-x-icu"
    
    def __init__(self, async_db: AsyncDatabase, entity_type: Type[EntityType]) -> None:
        self.entity_type = entity_type
        self._db = async_db
        self._primary_key = inspect(self.entity_type).primary_key[0]

    async def __set_tenant_id(self, session, tenant_id: str | None):
        """Sets the app.tenant_id in the database session safely."""
        if tenant_id:
            # IMPORTANT: Postgres SET command does NOT support bind parameters (:t_id).
            # We must use set_config function to safely use parameters in a session variable.
            await session.execute(
                text("SELECT set_config('app.tenant_id', :t_id, false)"),
                {"t_id": str(tenant_id)}
            )

    @property
    def primary_key(self):
        """Primary Key alanı"""
        return self._primary_key

    async def get(self, obj_id: Any, tenant_id: str | None = None, field_list: List[str] | None = None) -> EntityType:
        """Verilen object ID değerine karşılık gelen kaydı getirir
        """

        stmt = select(self.entity_type)
        if field_list and len(field_list) > 0:
            expand_list = self.__create_expand_list(field_list)
            rels = self.__find_relations(expand_list)
            stmt = self.__apply_relations(stmt, rels)

        stmt = stmt.filter(self._primary_key == obj_id)

        ret_val: EntityType
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)
            data = await session.execute(stmt)
            ret_val = data.unique().scalars().first()

        return ret_val

    async def find(self, query_args: QueryArgs, tenant_id: str | None = None) -> List[EntityType]:
        """Verilen sorgu parametrelerine göre modeli sorgular"""

        # TODO (kgulenc) 11-02-2023 1-M ilişkili verilerin çekilmesi durumunda limit ve offset değerleri
        # karışıyor. 1 parent kayda karşılık N tane child gelmesinden dolayı toplam kayıt sayısını N olarak
        # algılamasından dolayı limit ve offset hatalı çalışıyor. M -1 senaryosunda doğru çalışmasıyor.
        # Bu durum ileride düzeltilecek. ilk olarak id listesi olınacak sonra veri çekilecek

        stmt = select(self.entity_type)

        # Sorgu parametreleri sorgu cümlesine eklenir.
        stmt = self.__apply_query_args(stmt, query_args)

        if query_args.limit:
            stmt = stmt.limit(query_args.limit)

        if query_args.offset:
            stmt = stmt.offset(query_args.offset)

        ret_val: List[EntityType] = []
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)
            data = await session.execute(stmt)
            ret_val = data.unique().scalars().all()

        return ret_val

    async def count(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        """Verilen sorgu parametrelerine göre modeli sorgular"""

        count_args = query_args.model_copy()

        # Veriyi sınırlandıran offset ve limit değerleri kaldırılır.
        count_args.offset = 0
        count_args.limit = sys.maxsize
        count_args.order = None
        stmt = select(self.entity_type)

        # Sorgu parametreleri sorgu cümlesine eklenir.
        stmt = self.__apply_query_args(stmt, count_args)

        ret_val = 0
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)
            # 1-N ilişkili tabloların olması durumda sadece parent tablo kayıt sayısını
            # getirmesi için tekil alan kullanılır.
            stmt = stmt.distinct(self.primary_key)
            data = await session.execute(select(func.count()).select_from(stmt.subquery()))
            ret_val = data.scalar()

        return ret_val

    async def find_one(self, query_args: QueryArgs, tenant_id: str | None = None) -> EntityType:
        """Verilen sorgu parametrelerine uyan ilk kaydı getirir"""

        stmt = select(self.entity_type)

        # Sorgu parametreleri sorgu cümlesine eklenir.
        stmt = self.__apply_query_args(stmt, query_args)

        ret_val: EntityType = None  # type: ignore
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)
            data = await session.execute(stmt)
            ret_val = data.unique().scalars().first()

        return ret_val

    def dict(self, item: EntityType, fields: List[str] | None = None) -> Dict:
        """Model verisini field listesindeki öznitelikler baz alınarak yeni bir yapıya aktarır.
        M-1 ve M-1 ilişkili yapılara ait veriler ya obje olarak ya da liste olarak gönüştürülürler.
        Parent-Child ilişkilerinde liste, child-parent ilişkilerinde obje olarak dönüşüm yapılır
        """

        def inner_dict(model: EntityType, dictx: Any, field: Dict | str):
            if isinstance(field, str):
                val = getattr(model, field)
                dictx[field] = val
            else:
                # Eğer alt bir kırılım geliyorsa boş bir model oluşturulur
                # ve fonksiyon yeniden çağrılır
                val = getattr(model, field["name"])
                if not val:
                    dictx[field["name"]] = None
                else:
                    if isinstance(val, list):
                        # Eğer değer liste ise yeni bir liste oluşturulur ve yeni elemanlar listeye eklenir.
                        sub_list = []
                        dictx[field["name"]] = sub_list
                        for sub_val in val:
                            sub_dict = {}
                            sub_list.append(sub_dict)
                            for sub_field in field["fields"]:
                                inner_dict(sub_val, sub_dict, sub_field)
                    else:
                        sub_dict = {}
                        dictx[field["name"]] = sub_dict
                        for sub_field in field["fields"]:
                            inner_dict(val, sub_dict, sub_field)

        # Alanlar tanımlı değilse, modelin tanımlı kolonları getirilir
        # herhangi bir hiyerarşik bilgi getirilmez
        if not fields:
            mapper = inspect(self.entity_type)
            fields = [col.key for col in mapper.column_attrs]

        ret_val = {}
        field_list = self.__create_select_tree(fields)
        for field in field_list:
            inner_dict(item, ret_val, field)

        return ret_val

    async def create(self, create_dict: Dict[str, Any], tenant_id: str | None = None, user_id: str | None = None ) -> EntityType:
        """Yeni bir kayıt oluşturur"""

        # Oluşturma zamanı eklenir
        if hasattr(self.entity_type, "created_at"):
            create_dict["created_at"] = datetime.now()
  
        # Oluşturan user id eklenir
        if hasattr(self.entity_type, "creator_user_id"):
            create_dict["creator_user_id"] = user_id
                
        db_obj = self.entity_type(**create_dict)
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)
            db_obj.tenant_id = tenant_id

            session.add(db_obj)
            await session.commit()

        return db_obj

    async def create_all(self, create_dicts: List[Dict[str, Any]], tenant_id: str | None = None, user_id: str | None = None ) -> List[EntityType]:
        """Yeni kayıtları oluşturur"""
        db_objs: List[EntityType] = []
        for create_dict in create_dicts:
            # Oluşturma zamanı eklenir
            if hasattr(self.entity_type, "created_at"):
                create_dict["created_at"] = datetime.now()
                
            # Oluşturan user id eklenir
            if hasattr(self.entity_type, "creator_user_id"):
                create_dict["creator_user_id"] = user_id

            db_obj = self.entity_type(**create_dict)
            db_obj.tenant_id = tenant_id
            db_objs.append(db_obj)

        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)

            session.add_all(db_objs)
            await session.commit()

        return db_objs

    async def update(self, obj_id: Any, update_dict: Dict[str, Any], tenant_id: str | None = None, user_id: str | None = None ) -> EntityType:
        """Id si verilen kaydı günceller"""

        # Günceleme zamanı eklenir
        if hasattr(self.entity_type, "updated_at"):
            update_dict["updated_at"] = datetime.now()
            
        # Günceleyen user id eklenir
        if hasattr(self.entity_type, "updater_user_id"):
            update_dict["updater_user_id"] = user_id

        stmt = update_db(self.entity_type). \
            where(self._primary_key == obj_id). \
            values(update_dict)

        ret_val: int = 0
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)

            result = await session.execute(stmt)
            await session.commit()
            ret_val = result.rowcount

        if ret_val == 0:
            return None
        return await self.get(obj_id, tenant_id)

    async def update_by_ids(self, obj_ids: List[Any], update_dict: Dict[str, Any], tenant_id: str | None = None, user_id: str | None = None ) -> bool:
        # Günceleme zamanı eklenir
        if hasattr(self.entity_type, "updated_at"):
            update_dict["updated_at"] = datetime.now()

        # Günceleyen user id eklenir
        if hasattr(self.entity_type, "updater_user_id"):
            update_dict["updater_user_id"] = user_id
            
        stmt = update_db(self.entity_type)

        # Sorgu parametreleri sorgu cümlesine eklenir.
        stmt = self.__apply_query_args(stmt, QueryArgs(
            where=[
                Filter(field=self.primary_key.name,
                       op=FilterOp.IN, value=obj_ids)
            ]
        ))

        stmt = stmt.values(update_dict).execution_options(
            synchronize_session="fetch")

        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)

            result = await session.execute(stmt)
            ret_val = len(obj_ids) == result.rowcount
            result = await session.commit() if ret_val else await session.rollback()

        return ret_val

    async def update_all(self, query_args: QueryArgs, update_dict: Dict[str, Any], tenant_id: str | None = None, user_id: str | None = None ) -> int:
        """Sorgu parametelerine uyan kayıtları günceller"""

        # Günceleme zamanı eklenir
        if hasattr(self.entity_type, "updated_at"):
            update_dict["updated_at"] = datetime.now()

        # Günceleyen user id eklenir
        if hasattr(self.entity_type, "updater_user_id"):
            update_dict["updater_user_id"] = user_id
            
        stmt = update_db(self.entity_type)

        # Sorgu parametreleri sorgu cümlesine eklenir.
        stmt = self.__apply_query_args(stmt, query_args)

        stmt = stmt.values(update_dict).execution_options(
            synchronize_session="fetch")

        ret_val: int = 0
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)

            result = await session.execute(stmt)
            await session.commit()
            ret_val = result.rowcount

        return ret_val

    async def delete(self, obj_id: Any, tenant_id: str | None = None) -> bool:
        """obj_id değerindeki kaydı siler"""

        stmt = delete(self.entity_type)
        stmt = stmt.filter(self._primary_key == obj_id)
        ret_val = 0
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)

            result = await session.execute(stmt)
            await session.commit()
            ret_val = result.rowcount

        return ret_val == 1

    async def delete_by_ids(self, obj_ids: List[Any], tenant_id: str | None = None) -> int:
        """obj_ids listesindeki kayıtları siler"""

        stmt = delete(self.entity_type)
        stmt = stmt.filter(self._primary_key.in_(obj_ids))
        ret_val = 0
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)

            result = await session.execute(stmt)
            if len(obj_ids) == result.rowcount:
                await session.commit()
            else:
                await session.rollback()
            ret_val = result.rowcount

        return ret_val

    async def delete_all(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        """Verilen sorgu parametrelerine göre kayıtları siler"""

        select_stmt = select(self.primary_key)

        # Sorgu parametreleri sorgu cümlesine eklenir.
        select_stmt = self.__apply_query_args(select_stmt, query_args)

        stmt = delete(self.entity_type). \
            where(self.primary_key.in_(select_stmt.scalar_subquery()))

        stmt = stmt.execution_options(synchronize_session="fetch")
        ret_val: int = 0
        async with self._db.session() as session:
            await self.__set_tenant_id(session, tenant_id)

            result = await session.execute(stmt)
            await session.commit()
            ret_val = result.rowcount

        return ret_val
    
    def extract_fields_from_model(self, field_list: List[str], item: List[Any], parent_key: str | None):
        """Model olarak gelen alan listesini nokta formasyona çevirir. 
        ["id", "name", "sub_field": ["id", "name"]] => ["id", "name", "sub_field.id", "sub_field.name]
        """
        for sub_item in item:
            if isinstance(sub_item, dict):
                for k, v in sub_item.items():
                    self.extract_fields_from_model(
                        field_list, v, parent_key + "." + k if parent_key else k)
            else:
                field_list.append(parent_key + "." +
                                    sub_item if parent_key else sub_item)

    def __apply_query_args(self, stmt, query_args: QueryArgs) -> Any:
        """Sorgu parametrelerini sorgu cümlesine uygular"""

        field_list = self.__create_field_list(query_args)
        if len(field_list) > 0:
            expand_list = self.__create_expand_list(field_list)
            rels = self.__find_relations(expand_list)
            stmt = self.__apply_relations(stmt, rels)

        if query_args.where:
            stmt = self.__apply_filter(stmt, query_args.where, rels)

        if query_args.order:
            stmt = self.__apply_sort(stmt, query_args.order, rels)

        return stmt

    def __create_field_list(self, query_args: QueryArgs) -> List[str]:
        """QueryArgs içindeki filter, select ve sort parametrelerinden alan listesi oluşturur."""

        def extract_fields(field_list: List[str], filter_list: List[Union[Filter, FilterGroup]]) -> List[str]:
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
            self.extract_fields_from_model(model_fields, query_args.model, None)
            query_args.select = model_fields

        # select parametreleri eklenir
        if query_args.select:
            return_val.extend([
                x for x in query_args.select if x not in return_val
            ])

        # filter alanları eklenir
        if query_args.where:
            extract_fields(return_val, query_args.where)

        # Sort parametreleri eklenir
        if query_args.order:
            return_val.extend([
                key for key in query_args.order if key not in return_val
            ])

        return return_val

    def __create_expand_list(self, field_list: List) -> List[str]:
        """Alan listesindeki değerlere göre bir expand (join table) listesi oluşturur.
        Alan listesi select, filter ya da sort bölümlerinden gelen iç içe alanlar olabilir.
        iç içe alanlar kullanılarak bir expand listesi oluşturulur.
        "id",
        "invoices.id",
        "invoices.customer.id",
        "invoices.customer.name",

        Bu durumda oluşacak expand listesi ["invoice","customer"] olacaktır.
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

    def __create_select_tree(self, fields: List[str]) -> List:
        """Field listesini hiyerarşik ağaç yapısına dönüştürür. Veritabanından getirilmiş olan
        veriler bu hiyerarşiye göre dönüştürülürler. 

        Örnek Liste:
        "id",
        "invoices.id",
        "invoices.customer.id",
        "invoices.customer.name",

        Ağaç yapısına dönüşmüş hali       
        [
            "id",
            {
                "name": "invoices",
                "fields": [
                    "id",
                    {
                        "name": "customer",
                        "fields": [
                            "id",
                            "name"
                        ]
                    },
                ]
            },
        ]
        """
        def inner_func(f_list: List, field: str) -> List:
            field_parts = field.split(".")
            if len(field_parts) == 1:
                f_list.append(field_parts[0])
            else:
                field_obj = next(
                    (f for f in f_list if isinstance(f, dict)
                     and f["name"] == field_parts[0]), None
                )
                if not field_obj:
                    field_obj = {
                        "name": field_parts[0],
                        "fields": []
                    }
                    f_list.append(field_obj)

                new_fields = ".".join(field_parts[1:])
                inner_func(field_obj["fields"], new_fields)

        ret_val = []
        for field in fields:
            inner_func(ret_val, field)
        return ret_val

    def __apply_relations(self, stmt, rels: Any) -> Any:
        """expand listesindeki property listesini join olarak modele ekler
            model.customer
            model.invoices.company
        Args:
            stmt (Any): join lerin yapılacağı select
            rels (List[str]): expand ve eager ilişki listesi

        Returns:
            Any: eklemeler yapıldıktan sonra statement aynı şekilde döndürülür
        """
        # Joinler eklenir
        join_grps = rels[0]
        for key in join_grps:
            join_grp = join_grps.get(key)
            # Join olarak eklenen model ile ana model aynı ise join yapılmaz
            if join_grp['model'] != self.entity_type:
                stmt = stmt.outerjoin(join_grp['attr'])

        # Contain_eager ilişkileri eklenir
        eagers = rels[1]
        stmt = stmt.options(*eagers)

        return stmt

    def __find_relations(self, expand: List[str]) -> Any:
        """expand listesindeki property listesini join olarak modele ekler

        Args:
            expand (List[str]): expand listesi
        Returns:
            Any: join ve eager ilişki listesini oluşturur.
        """
        join_grps = OrderedDict()
        eagers = list()
        for rel in expand:
            attr_names = rel.split(".")
            in_model = self.entity_type
            contains: Any = None
            for attr_name in attr_names:
                in_attr = getattr(in_model, attr_name)
                in_model = in_attr.mapper.class_
                key = join_grps.get(attr_name)
                if not key:
                    key = {
                        "attr": in_attr,
                        "model": in_model,
                        "path": rel
                    }
                    join_grps[attr_name] = key

                contains = contains.contains_eager(
                    in_attr) if contains else contains_eager(in_attr)

            eagers.append(contains)

        return join_grps, eagers

    def __apply_filter(self, stmt, filters: List[Union[Filter, FilterGroup]], rels: Any = None) -> Any:
        """Filtreleri sorgu cümlesine ekler. Filtreler hiyerarşik modelde olabilir
        filter(and(a_filter, b_filter, or(c_filter, d_filter)), e_filter)
        """

        def apply_filter(filter_list: List, filtery: Filter | FilterGroup, join_grps):
            if filtery.type == "filter":
                # Eğer alt kırılım yoksa direk olarak modeldeki öznitelik kullanılır
                filter_attr = None
                if "." not in filtery.field:
                    filter_attr = getattr(self.entity_type, filtery.field)
                else:
                    # ilgili alanın hangi joine ait olduğu ve ilgili model bulunur
                    fields = filtery.field.split(".")
                    # Son alan attribute ismidir
                    rel_field = fields.pop()
                    expand = ".".join(fields)
                    rel_model = next(
                        (join_grps[key]["model"]
                         for key in join_grps if join_grps[key]["path"] == expand), None
                    )
                    if rel_model:
                        filter_attr = getattr(rel_model, rel_field)
                    else:
                        raise ValueError(filtery)
                # (TODO) kgulenc Exceptionlar düzenlenecek
                if not filter_attr:
                    raise ValueError(filtery)

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
                    case FilterOp.CONTAINS:
                        filter_list.append(filter_attr.contains(cast_value))
                    case _:
                        raise ValueError(f"Unknown filter operator: {filtery.op}")
            else:
                sub_filter_list = []
                for filterz in filtery.filters:
                    apply_filter(sub_filter_list, filterz, join_grps)
                if filtery.type == FilterType.AND:
                    filter_list.append(and_(*sub_filter_list))
                else:
                    filter_list.append(or_(*sub_filter_list))

        join_grps = rels[0] if rels else {}
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
                ret_obj = val if type(val) == value_type else value_type(str(val))
            return ret_obj

        ret_val = value
        value_type = filter_attr.type.python_type
        if type(value) == list:
            ret_val = [create_value_object(value_type, item) for item in value]
        else:
            ret_val = value if type(
                    value) == value_type else create_value_object(value_type, value)
        return ret_val

    def __apply_sort(self, stmt, sort: Dict[str, str], rels: Any = None) -> Any:
        """Sorguya sıralama kriterlerini ekler"""

        join_grps = rels[0] if rels else {}
        order_list = []
        for field_expr in sort:
            direction = sort[field_expr]
            sort_attr = None
            if "." not in field_expr:
                sort_attr = getattr(self.entity_type, field_expr)
            else:
                # ilgili alanın hangi joine ait olduğu ve ilgili model bulunur
                fields = field_expr.split(".")
                # Son alan attribute ismidir
                rel_field = fields.pop()
                expand = ".".join(fields)
                rel_model = next(
                    (join_grps[key]["model"]
                        for key in join_grps if join_grps[key]["path"] == expand), None
                )
                if rel_model:
                    sort_attr = getattr(rel_model, rel_field)
                else:
                    raise ValueError(field_expr)
            # (TODO) kgulenc Exceptionlar düzenlenecek
            if not sort_attr:
                raise ValueError(field_expr)
            
            # Text ya da Char alanlara locale eklenir
            sort_attr = self.__set_locale(sort_attr, self.LOCALE_NAME)
            order_list.append(sort_attr.desc() if direction.lower()
                              == "desc" else sort_attr.asc())

        if len(order_list) > 0:
            stmt = stmt.order_by(*order_list)

        return stmt

    def __set_locale(self, sort_attr: Any, locale_name: str) -> Any:
        if isinstance(sort_attr.type, VARCHAR) or \
            isinstance(sort_attr.type, NVARCHAR) or \
            isinstance(sort_attr.type, TEXT) or \
            isinstance(sort_attr.type, Text) or \
            isinstance(sort_attr.type, CHAR) or \
            isinstance(sort_attr.type, NCHAR):
            sort_attr = sort_attr.collate(locale_name)
        return sort_attr