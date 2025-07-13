from functools import cache
import json
from typing import Any, Dict, List
from pydantic import TypeAdapter
from sqlalchemy import text
from sqlalchemy.engine import URL
from mapa.core.data.query_args import (
    Filter,
    FilterGroup,
    FilterOp,
    FilterType,
    QueryArgs,
)
from mapa.core.data.result import ActionResult, PagingResult
from mapa.gateway.connection_info.authentication_info_model import (
    BasicAuthAuthenticationInfo,
)
from httpx import AsyncClient, Request, BasicAuth
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo
from mapa.gateway.connection_info.database_info_model import DatabaseInfo
from mapa.gateway.integration.integration_model import (
    AdHocQueryConnection,
    ElasticBackendConnection,
)
from mapa.gateway.constant import AuthenticationInfoTypes, MethodTypes, SqlResultTypes
from mapa.gateway.route.route_model import Route
from service.integration_handler.integration_handler import IntegrationHandler
from service.integration_handler.table_repository import TableDesc, TableRepository
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from pydantic import TypeAdapter
import json


class ElasticIntegrationHandler(IntegrationHandler):
    def __init__(self, route: Route, path_params: Dict[str, Any]):
        super().__init__(route=route, path_params=path_params)
        self.es_client = None

    async def execute(self, service_request: ServiceRequest) -> ServiceResponse:
        if not self.integration.connection_info:
            raise ValueError("ConnectionInfo not defined")

        # Authentication yapısı oluşturulur.
        conn_info: ConnectionInfo = self.integration.connection_info  # type: ignore
        http_conn = ElasticBackendConnection(**(self.integration.connection))
        auth = self._create_auth(conn_info)
        headers = self._build_headers(service_request.headers)
        self.es_client = AsyncElasticsearch(
            hosts=self.__convert_to_array(http_conn.endpoint),
            http_auth=auth,
            headers=headers,
        )
        try:
            body = await self._execute_document(
                conn_info.params, http_conn, service_request
            )

            # Servis dönüş değeri oluşturulur.
            response = ServiceResponse(
                status_code=200, response_type="application/json", body=dict(body)
            )
            return response
        finally:
            await self.es_client.close()

    async def _execute_document(
        self,
        elastic_conn: dict,
        http_conn: ElasticBackendConnection,
        service_request: ServiceRequest,
    ):
        # Post metodu dışındaki metodlar query parametresini kullanılır.
        params = {**service_request.path_params, **service_request.query_params}

        index = http_conn.index_name
        if not index:
            raise ValueError("Index bilgisi eksik")

        ret_val = {}
        try:
            match service_request.method:
                case MethodTypes.GET:
                    # ElasticSearch'te doküman sorgulama
                    ret_val = await self.__execute_es_get(http_conn.index_name, params)
                case MethodTypes.POST:
                    # ElasticSearch'e doküman ekleme
                    ret_val = await self.__execute_es_post(
                        http_conn.index_name, params, service_request.body
                    )
                case MethodTypes.PUT:
                    # ElasticSearch'teki dokümanı güncelleme
                    ret_val = await self.__execute_es_put(
                        http_conn.index_name, params, service_request.body
                    )
                case MethodTypes.DELETE:
                    # ElasticSearch'ten doküman silme
                    ret_val = await self.__execute_es_delete(
                        http_conn.index_name, params
                    )
                case _:
                    raise ValueError(
                        f"Method {service_request.method} is not supported."
                    )
        except Exception as e:
            ret_val = {"error": str(e)}

        return ret_val

    def _create_auth(self, connection_info: ConnectionInfo) -> Any:
        if connection_info and connection_info.params:
            # auth type BASICAUTH ise kimlik bilgileri döndürülür.
            if connection_info.params["type"] == AuthenticationInfoTypes.BASICAUTH:
                return (
                    connection_info.params["auth_params"]["username"],
                    connection_info.params["auth_params"]["password"],
                )
            elif connection_info.params["type"] == AuthenticationInfoTypes.APIKEY:
                api_key: str = connection_info.params["auth_params"]["api_key"]
                return {"Authorization": f"ApiKey {api_key}"}
            else:
                return None
        return None

    def _build_headers(self, req_headers: Any) -> dict[str, str]:
        headers = {}
        if req_headers.get("content-type") is not None:
            headers["Content-Type"] = req_headers.get("content-type")
        return headers

    async def __execute_es_get(self, index, params):
        """
        Elasticsearch GET işlemi, QueryArgs kullanır ve PagingResult döndürür.
        """
        try:
            # QueryArgs doğrulama ve dönüştürme
            query_args: QueryArgs = TypeAdapter(QueryArgs).validate_python(
                json.loads(params["query"])
            )
            es_query = self.__convert_query_args_to_elastic_query(query_args)

            # Elasticsearch sorgusu
            response = await self.es_client.search(index=index, body=es_query)

            # Toplam doküman sayısını al
            total_hits = response["hits"]["total"]["value"]

            # Dokümanları al ve düzelt
            documents = [
                {**doc["_source"], "_id": doc["_id"]}
                for doc in response["hits"]["hits"]
            ]

            # PagingResult döndür
            return PagingResult(
                total=total_hits,
                items=documents,
                offset=query_args.offset,
                limit=query_args.limit,
            )
        except NotFoundError:
            raise
        except Exception as e:
            raise e

    async def __execute_es_post(self, index, params, body):
        # Yeni bir doküman ekleme
        try:
            response = await self.es_client.index(index=index, body=body)
            return response
        except Exception as e:
            raise e

    async def __execute_es_put(self, index, params, body):
        """
        QueryArgs kullanarak Elasticsearch PUT işlemi.
        """
        query_args: QueryArgs = TypeAdapter(QueryArgs).validate_python(
            json.loads(params["query"])
        )
        es_query = self.__convert_query_args_to_elastic_query(query_args)

        if not body:
            raise ValueError("Güncelleme için 'body' parametresi gerekli")

        try:
            response = await self.es_client.update_by_query(
                index=index,
                body={
                    "query": es_query,
                    "script": {"source": "ctx._source.putAll(params)", "params": body},
                },
            )
            return ActionResult(
                success=True,
                affected=response.get("updated", 0),
                message="Dokümanlar başarıyla güncellendi.",
            )
        except Exception as e:
            raise e

    async def __execute_es_delete(self, index, params):
        """
        QueryArgs kullanarak Elasticsearch DELETE işlemi.
        """
        query_args: QueryArgs = TypeAdapter(QueryArgs).validate_python(
            json.loads(params["query"])
        )
        es_query = self.__convert_query_args_to_elastic_query(query_args)

        try:
            response = await self.es_client.delete_by_query(
                index=index,
                body={"query": es_query},
            )
            return ActionResult(
                success=True,
                affected=response.get("deleted", 0),
                message="Dokümanlar başarıyla silindi.",
            )
        except Exception as e:
            return ActionResult(
                success=False,
                affected=0,
                message=f"Silme işlemi sırasında hata oluştu: {str(e)}",
            )

    def __convert_to_array(self, endpoint_string: str) -> list[str]:
        # Virgül ile ayrılmışsa split yaparak liste oluştur
        if "," in endpoint_string:
            return endpoint_string.split(",")
        # Tek bir endpoint ise listeye çevir
        return [endpoint_string]

    def __convert_filter_to_query(self, filter: Filter) -> Dict[str, Any]:
        """Tek bir Filter objesini Elasticsearch query'e çevirir."""
        op = filter.op
        field = filter.field
        value = filter.value

        # .keyword eklenecek alanları burada belirleyebilirsin (isteğe bağlı filtreleme için)
        EXACT_MATCH_OPS = {
            FilterOp.EQUAL,
            FilterOp.NOT_EQUAL,
            FilterOp.IN,
            FilterOp.NOT_IN,
        }

        def keyword_field(f: str) -> str:
            # Otomatik olarak `.keyword` eklenir sadece exact match gereken operatörlerde
            return f"{f}.keyword" if op in EXACT_MATCH_OPS else f

        if op == FilterOp.EQUAL:
            return {"term": {keyword_field(field): value}}
        elif op == FilterOp.NOT_EQUAL:
            return {"bool": {"must_not": {"term": {keyword_field(field): value}}}}
        elif op == FilterOp.IN:
            return {"terms": {keyword_field(field): value}}
        elif op == FilterOp.NOT_IN:
            return {"bool": {"must_not": {"terms": {keyword_field(field): value}}}}
        elif op == FilterOp.NULL:
            return {"bool": {"must_not": {"exists": {"field": field}}}}
        elif op == FilterOp.NOT_NULL:
            return {"exists": {"field": field}}
        elif op == FilterOp.LESS_THAN:
            return {"range": {field: {"lt": value}}}
        elif op == FilterOp.LESS_THAN_OR_EQUAL:
            return {"range": {field: {"lte": value}}}
        elif op == FilterOp.MORE_THAN:
            return {"range": {field: {"gt": value}}}
        elif op == FilterOp.MORE_THAN_OR_EQUAL:
            return {"range": {field: {"gte": value}}}
        elif op == FilterOp.LIKE or op == FilterOp.ILIKE:
            return {"wildcard": {field: f"*{value}*"}}
        elif op == FilterOp.NOT_LIKE or op == FilterOp.NOT_ILIKE:
            return {"bool": {"must_not": {"wildcard": {field: f"*{value}*"}}}}
        elif op == FilterOp.BETWEEN:
            if isinstance(value, list) and len(value) == 2:
                return {"range": {field: {"gte": value[0], "lte": value[1]}}}
            raise ValueError("BETWEEN requires a list of two values.")
        else:
            raise NotImplementedError(f"Operation {op} is not implemented.")

    def __convert_filter_group_to_query(self, group: FilterGroup) -> Dict[str, Any]:
        """FilterGroup objesini Elasticsearch query'e çevirir."""
        bool_type = "must" if group.type == FilterType.AND else "should"
        filters = []

        for item in group.filters:
            if isinstance(item, Filter):
                filters.append(self.__convert_filter_to_query(item))
            elif isinstance(item, FilterGroup):
                filters.append(self.__convert_filter_group_to_query(item))

        return {"bool": {bool_type: filters}}

    def __convert_query_args_to_elastic_query(self, args: QueryArgs) -> Dict[str, Any]:
        """QueryArgs objesini Elasticsearch Query DSL'e çevirir."""
        query: Dict[str, Any] = {"query": {"bool": {}}}

        # WHERE koşulları
        if args.where:
            must_conditions = []
            for condition in args.where:
                if isinstance(condition, Filter):
                    must_conditions.append(self.__convert_filter_to_query(condition))
                elif isinstance(condition, FilterGroup):
                    must_conditions.append(
                        self.__convert_filter_group_to_query(condition)
                    )
            if must_conditions:
                query["query"]["bool"]["must"] = must_conditions

        # Eğer WHERE koşulları boşsa, 'match_all' sorgusu kullanılır
        if not query["query"]["bool"]:
            query["query"] = {"match_all": {}}

        # kontrol edilecek
        # ORDER BY
        no_keywords_fields = {"@timestamp", "created_at", "updated_at"}
        if args.order:
            query["sort"] = [
                {
                    (
                        field
                        if field in no_keywords_fields or field.endswith(".keyword")
                        else f"{field}.keyword"
                    ): {"order": direction}
                }
                for field, direction in args.order.items()
            ]

        # LIMIT ve OFFSET
        query["from"] = args.offset if args.offset else 0
        query["size"] = args.limit if args.limit else 10  # Varsayılan limit: 10

        # SELECT (Bir alan listesi verilirse)
        if args.select:
            query["_source"] = args.select

        return query
