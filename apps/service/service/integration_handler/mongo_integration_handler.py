import json
from pydantic import TypeAdapter
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any, Dict, List
from mapa.core.data.query_args import (
    QueryArgs,
    Filter,
    FilterGroup,
    FilterOp,
    FilterType,
)
from mapa.core.data.result import ActionResult, PagingResult
from mapa.gateway.connection_info.database_info_model import DatabaseInfo
from mapa.gateway.integration.integration_model import MongoBackendConnection
from service.integration_handler.integration_handler import IntegrationHandler
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse
from mapa.gateway.route.route_model import Route


class MongoIntegrationHandler(IntegrationHandler):
    def __init__(self, route: Route, path_params: Dict[str, Any]):
        super().__init__(route=route, path_params=path_params)
        self.client = None
        self.db = None

    async def execute(self, service_request: ServiceRequest) -> ServiceResponse:
        # Post metodu dışındaki metodlar query parametresini kullanılır.
        params = {**service_request.path_params, **service_request.query_params}

        mongo_conn = MongoBackendConnection(**(self.integration.connection))
        collection_name = mongo_conn.collection_name
        if not collection_name:
            raise ValueError("Collection bilgisi eksik")

        db_conn = DatabaseInfo(**self.integration.connection_info.params)  # type: ignore

        conn_uri = f"{db_conn.dialect}://"
        if db_conn.username and db_conn.password:
            conn_uri += f"{db_conn.username}:{db_conn.password}@"
        conn_uri += f"{db_conn.host or 'localhost'}:{db_conn.port or 27017}/"
        conn_uri += f"{db_conn.database or 'admin'}"

        self.client = AsyncIOMotorClient(conn_uri)
        try:
            if not db_conn.database:
                raise ValueError("Database bilgisi eksik")
            self.db = self.client[db_conn.database]

            if not collection_name:
                raise ValueError("Collection bilgisi eksik")
            collection = self.db[collection_name]
            ret_val = {}
            # İşlemi belirler
            match service_request.method:
                case "GET":
                    query_args: QueryArgs = TypeAdapter(QueryArgs).validate_python(
                        json.loads(params["query"])
                    )
                    mongo_query = self.__convert_query_args_to_mongo_query(query_args)
                    # `select` parametresini işleyerek projection oluşturma
                    projection = (
                        {field: 1 for field in query_args.select}
                        if query_args.select
                        else None
                    )
                    total_documents = await collection.count_documents(mongo_query)
                    cursor = (
                        collection.find(mongo_query, projection)
                        .skip(query_args.offset or 0)
                        .limit(query_args.limit or 10)
                    )
                    documents = await cursor.to_list(length=query_args.limit or 10)
                    ret_val = PagingResult(
                        total=total_documents,
                        items=documents,
                        offset=query_args.offset,
                        limit=query_args.limit,
                    )
                case "POST":
                    body = service_request.body
                    if isinstance(body, str):
                        body = json.loads(body)
                    result = await collection.insert_one(body)
                    ret_val = ActionResult(
                        success=True,
                        affected=len(result.inserted_id),
                        message="Dokümanlar başarıyla eklendi.",
                    )

                case "PUT":
                    query_args: QueryArgs = TypeAdapter(QueryArgs).validate_python(
                        json.loads(params["query"])
                    )
                    mongo_query = self.__convert_query_args_to_mongo_query(query_args)
                    body = service_request.body
                    if not body:
                        raise ValueError("PUT işlemi için 'body' parametresi gerekli")
                    if isinstance(body, str):
                        body = json.loads(body)

                    result = await collection.update_many(mongo_query, {"$set": body})
                    ret_val = ActionResult(
                        success=True,
                        affected=result.matched_count,
                        message="Dokümanlar başarıyla güncellendi.",
                    )
                case "DELETE":
                    query_args: QueryArgs = TypeAdapter(QueryArgs).validate_python(
                        json.loads(params["query"])
                    )
                    mongo_query = self.__convert_query_args_to_mongo_query(query_args)
                    result = await collection.delete_many(mongo_query)
                    ret_val = ActionResult(
                        success=True,
                        affected=result.deleted_count,
                        message="Dokümanlar başarıyla silindi.",
                    )
                case _:
                    raise ValueError(f"Method {service_request.method} is not supported.")

            response = ServiceResponse(
                status_code=200, response_type="application/json", body=dict(ret_val)
            )
            return response
        finally:
            self.client.close()

    def __convert_query_args_to_mongo_query(self, args: QueryArgs) -> Dict[str, Any]:
        """QueryArgs objesini MongoDB Query'e çevirir."""
        mongo_query = {}

        # WHERE koşulları
        if args.where:
            and_conditions = []
            for condition in args.where:
                if isinstance(condition, Filter):
                    and_conditions.append(self.__convert_filter_to_query(condition))
                elif isinstance(condition, FilterGroup):
                    and_conditions.append(
                        self.__convert_filter_group_to_query(condition)
                    )
            if and_conditions:
                mongo_query["$and"] = and_conditions

        return mongo_query

    def __convert_filter_to_query(self, filter: Filter) -> Dict[str, Any]:
        """Filter objesini MongoDB query'ye çevirir."""
        op = filter.op
        field = filter.field
        value = filter.value

        if op == FilterOp.EQUAL:
            return {field: value}
        elif op == FilterOp.NOT_EQUAL:
            return {field: {"$ne": value}}
        elif op == FilterOp.IN:
            return {field: {"$in": value}}
        elif op == FilterOp.NOT_IN:
            return {field: {"$nin": value}}
        elif op == FilterOp.NULL:
            return {field: {"$exists": False}}
        elif op == FilterOp.NOT_NULL:
            return {field: {"$exists": True}}
        elif op == FilterOp.LESS_THAN:
            return {field: {"$lt": value}}
        elif op == FilterOp.LESS_THAN_OR_EQUAL:
            return {field: {"$lte": value}}
        elif op == FilterOp.MORE_THAN:
            return {field: {"$gt": value}}
        elif op == FilterOp.MORE_THAN_OR_EQUAL:
            return {field: {"$gte": value}}
        else:
            raise NotImplementedError(f"Operation {op} is not implemented.")

    def __convert_filter_group_to_query(self, group: FilterGroup) -> Dict[str, Any]:
        """FilterGroup objesini MongoDB query'ye çevirir."""
        group_type = "$and" if group.type == FilterType.AND else "$or"
        filters = []

        for item in group.filters:
            if isinstance(item, Filter):
                filters.append(self.__convert_filter_to_query(item))
            elif isinstance(item, FilterGroup):
                filters.append(self.__convert_filter_group_to_query(item))

        return {group_type: filters}
