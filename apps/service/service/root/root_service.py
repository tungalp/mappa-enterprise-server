from functools import reduce
import json
from typing import Any, Dict, List, Tuple
from uuid import UUID
from urllib.parse import parse_qs, parse_qsl, urlparse
from fastapi import Request, Response
from sqlalchemy import text
from mapa.gateway.messaging.producer.service_messenger import ServiceMessenger
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_db_service import BaseDbService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from starlette.routing import Match
from fastapi.routing import APIRoute
from fastapi.responses import PlainTextResponse, JSONResponse, HTMLResponse
from mapa.gateway.connection_info.connection_info_service import ConnectionInfoService
import hashlib
import redis.asyncio as aioredis
from fastapi_cache import FastAPICache
from service.cache.cache_config import get_cache_config_from_env
from mapa.gateway.context_var.context_var_service import ContextVarService
from mapa.gateway.gateway_api.gateway_api_model import GatewayApi
from mapa.gateway.gateway_api.gateway_api_service import GatewayApiService
from mapa.gateway.parameter_mapping.parameter_mapping_model import RequestResponseMapping
from mapa.gateway.route.route_model import Route
from mapa.gateway.constant import (
    IntegrationTypes,
    ModifierTypes,
    ParameterMappingTypes,
    ValueTypes,
    MethodTypes,
)
from service.integration_handler.adhoc_query_integration_handler import (
    AdHocQueryIntegrationHandler,
)
from service.integration_handler.async_adhoc_query_integration_handle import (
    AsyncAdHocQueryIntegrationHandler,
)
from service.integration_handler.elastic_integration_handler import (
    ElasticIntegrationHandler,
)
from service.integration_handler.http_integration_handler import HttpIntegrationHandler
from service.integration_handler.integration_handler import IntegrationHandler
from service.integration_handler.mongo_integration_handler import (
    MongoIntegrationHandler,
)
from service.integration_handler.soap_integration_handler import SoapIntegrationHandler
from service.integration_handler.spatial.spatial_integration_handler import (
    SpatialIntegrationHandler,
)
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse
from service.model.scope import ServiceScope


class JSONResponseX(JSONResponse):
    """Datetime nesnesini problemsiz json dönüştürebilmesi için oluşturuldu"""

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")


def dummy_endpoint_func(request: Request) -> Response:
    """ApiRoute için kullanılacak dummy response handler fonksiyonu"""
    return PlainTextResponse(f"Hello, world!")


ALL_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]


class RootService(BaseDbService):

    def __init__(
        self,
        async_db: AsyncDatabase,
        gateway_api_service: GatewayApiService,
        connection_info_service: ConnectionInfoService,
        context_var_service: ContextVarService,
        messenger: ServiceMessenger,
    ) -> None:
        super().__init__(async_db)
        self._gateway_api_service = gateway_api_service
        self._connection_info_service = connection_info_service
        self._context_var_service = context_var_service
        self._messenger = messenger

        # Cache configuration from environment
        self._cache_config = get_cache_config_from_env()
        self._cache_ttl_tenant = self._cache_config.tenant_ttl
        self._cache_ttl_api = self._cache_config.api_ttl
        self._cache_ttl_api_details = self._cache_config.api_details_ttl

    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate a consistent cache key from prefix and arguments"""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def _get_from_cache(self, key: str):
        """Get data from Redis cache"""
        try:
            redis_read: aioredis.Redis = FastAPICache.get_backend().redis
            cached_data = await redis_read.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception:
            # If cache fails, continue without caching
            pass
        return None

    async def _set_cache(self, key: str, data: Any, ttl: int):
        """Set data in Redis cache with TTL"""
        try:
            redis_write: aioredis.Redis = FastAPICache.get_backend().redis
            await redis_write.set(key, json.dumps(data, default=str), ex=ttl)
        except Exception:
            # If cache fails, continue without caching
            pass

    async def find_tenant_id(self, tenant_name: str) -> UUID | None:
        """Tenant isminden tenant_id değerini döndürür - with caching"""
        # Check cache first
        cache_key = self._get_cache_key("tenant_id", tenant_name)
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            return UUID(cached_result) if cached_result else None

        # If not in cache, fetch from database
        qa = QueryArgs(
            where=[Filter(field="name", op=FilterOp.ILIKE, value=tenant_name)],
        ).to_serialize()
        response = await self._messenger.tenant_find(qa)
        tenants = response.get("tenants", [])
        tenant_id = tenants[0]["id"] if tenants else None

        # Cache the result
        await self._set_cache(cache_key, str(tenant_id) if tenant_id else None, self._cache_ttl_tenant)

        return tenant_id

    async def find_api(self, tenant_id: str, api_name: str) -> GatewayApi | None:
        """Tenant id ve api isminden Api bulur - with caching"""
        # Check cache first
        cache_key = self._get_cache_key("api", tenant_id, api_name)
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            return GatewayApi.model_validate(cached_result) if cached_result else None

        # If not in cache, fetch from database
        api = await self._gateway_api_service.find_one(
            QueryArgs(where=[Filter(field="path", op=FilterOp.EQUAL, value=api_name)]),
            tenant_id,
        )

        # Cache the result
        api_dict = api.model_dump() if api else None
        await self._set_cache(cache_key, api_dict, self._cache_ttl_api)

        return api

    async def get_api_with_details(self, tenant_id: str, api_id: UUID) -> GatewayApi:
        """İlgili Api nin tüm detay bilgilerini getirir - with caching"""
        # Check cache first
        cache_key = self._get_cache_key("api_details", tenant_id, str(api_id))
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            return GatewayApi.model_validate(cached_result)

        # If not in cache, fetch from database
        api = await self._gateway_api_service.get(
            api_id,
            tenant_id,
            [
                "id",
                "name",
                "type",
                "path",
                "identifier",
                "created_at",
                "context",
                {
                    "routes": [
                        "id",
                        "path",
                        "query",
                        "scope",
                        "method_type",
                        "cache_timeout",
                        "rate_limit",
                        "rate_second",
                        "retry_count",
                        "retry_millisecond",
                        "full_logging",
                        "gateway_api_id",
                        "integration_id",
                        {
                            "integration": [
                                "id",
                                "name",
                                "type",
                                "connection",
                                "gateway_api_id",
                                "timeout_in_millis",
                                "context",
                                {
                                    "connection_info": ["id", "name", "params", "type"],
                                    "parameter_mappings": [
                                        "id",
                                        "status_code",
                                        "type",
                                        "integration_id",
                                        "param_list",
                                        "created_at",
                                    ],
                                },
                            ]
                        },
                    ]
                },
            ],
        )

        # Cache the result
        api_dict = api.model_dump()
        await self._set_cache(cache_key, api_dict, self._cache_ttl_api_details)

        return api

    async def invalidate_tenant_cache(self, tenant_name: str):
        """Invalidate tenant cache for a specific tenant"""
        try:
            cache_key = self._get_cache_key("tenant_id", tenant_name)
            redis_write: aioredis.Redis = FastAPICache.get_backend().redis
            await redis_write.delete(cache_key)
        except Exception:
            pass

    async def invalidate_api_cache(self, tenant_id: str, api_name: str):
        """Invalidate API cache for a specific API"""
        try:
            cache_key = self._get_cache_key("api", tenant_id, api_name)
            redis_write: aioredis.Redis = FastAPICache.get_backend().redis
            await redis_write.delete(cache_key)
        except Exception:
            pass

    async def invalidate_api_details_cache(self, tenant_id: str, api_id: UUID):
        """Invalidate API details cache for a specific API"""
        try:
            cache_key = self._get_cache_key("api_details", tenant_id, str(api_id))
            redis_write: aioredis.Redis = FastAPICache.get_backend().redis
            await redis_write.delete(cache_key)
        except Exception:
            pass

    async def invalidate_context_var_cache(self, tenant_id: str):
        """Invalidate context variables cache for a specific tenant"""
        try:
            cache_key = self._get_cache_key("context_var", tenant_id)
            redis_write: aioredis.Redis = FastAPICache.get_backend().redis
            await redis_write.delete(cache_key)
        except Exception:
            pass

    async def invalidate_all_tenant_caches(self, tenant_id: str):
        """Invalidate all caches related to a tenant"""
        try:
            redis_write: aioredis.Redis = FastAPICache.get_backend().redis
            # Use pattern matching to find all keys for this tenant
            pattern = f"*{tenant_id}*"
            keys = await redis_write.keys(pattern)
            if keys:
                await redis_write.delete(*keys)
        except Exception:
            pass

    def find_handler(
        self, api: GatewayApi, path: str, method: str
    ) -> IntegrationHandler | None:
        """Gelen isteğin dizin yapısına uyan route ve bu routa karşılık gelen integration bulunur"""

        route_list = self._create_routes(api.routes or [])
        for route, api_route in route_list:
            match, scope = api_route.matches(
                {"type": "http", "path": path, "method": method}
            )
            # Bir eşleşme bulunduğunda Gelen istek için dönüş değerini oluşturacak handler döndürülür.
            if match == Match.FULL or (
                match == Match.PARTIAL and method in api_route.methods
            ):
                return self._create_handler_model(
                    route, api_route, scope.get("path_params")
                )

    async def find_context_var(self, tenant_id: str) -> Dict[str, Any]:
        """İlgili tenant da tanımlanmış olan tüm context değişkenlerini getirir - with caching"""
        # Check cache first
        cache_key = self._get_cache_key("context_var", tenant_id)
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        # If not in cache, fetch from database
        context_var_list = await self._context_var_service.find(QueryArgs(), tenant_id)
        result = {context_var.key: context_var.value for context_var in context_var_list}

        # Cache the result
        await self._set_cache(cache_key, result, self._cache_ttl_tenant)

        return result

    async def create_service_request(
        self, request: Request, handler: IntegrationHandler, data: Dict[str, Any]
    ) -> ServiceRequest:
        """Handler nesnesine gönderilecek olan ServiceRequest nesnesini oluşturur."""

        path = data["path"]
        context = data["context"]
        raw_body = await request.body()
        context["tenant_id"] = (
            request.user.tenant_id if request.user.is_authenticated else ""
        )
        context["user_id"] = request.user.sub if request.user.is_authenticated else ""

        # Not : Content Type Xml gelen bodyler doğrudan aktarılmıştır. (27.09.2023)
        if (
            request.headers.get("content-type") == "application/json"
            or request.headers.get("content-type") == "application/json; charset=utf-8"
        ):
            body = json.loads(raw_body if raw_body else "{}")
        elif request.headers.get("content-type") == "application/xml":
            body = raw_body
        else:
            parsed_qs = parse_qsl(raw_body.decode("utf-8"))  # type: ignore
            body = dict((x, y) for x, y in parsed_qs)

        return ServiceRequest(
            method=request.method,
            cookies=request.cookies,
            client=request.client,
            headers=dict(request.headers.items()),
            raw_path=request.url.path,
            path=path,
            path_params=handler.path_params,
            query_string=request.url.query,
            query_params=dict(request.query_params.items()),
            context=context,
            body=body,
        )

    def modify_service_request(
        self, service_request: ServiceRequest, handler: IntegrationHandler
    ) -> ServiceRequest:
        """Handler nesnesinden gelen response nesnesini düzenler."""

        ret_request = service_request.model_copy()

        scope = ServiceScope(
            header=ret_request.headers,
            path=handler.path_params,
            query=ret_request.query_params,
            body=ret_request.body,
            context=ret_request.context,
        )
        # Soap Headers'ta content type vb gibi parametreler hata yaratıyor.
        if isinstance(handler, SoapIntegrationHandler):
            scope.header = {}  # type: ignore

        # Parametre eşleştirmesi ve modifikasyonları yapılır.
        modified_scope = self._modify_scope(
            handler, scope, ParameterMappingTypes.REQUEST
        )

        ret_request.headers = modified_scope.header
        ret_request.body = modified_scope.body
        ret_request.path_params = modified_scope.path or {}
        ret_request.query_params = modified_scope.query or {}

        ret_request.headers.update(ret_request.context)

        return ret_request

    def modify_service_response(
        self, service_response: ServiceResponse, handler: IntegrationHandler
    ) -> ServiceResponse:
        """Handler nesnesinden gelen response nesnesini düzenler."""

        ret_response = service_response.model_copy()

        scope = ServiceScope(
            header=service_response.headers,
            body=service_response.body or {},
            status_code=service_response.status_code,
            context=ret_response.context,
        )

        # Parametre eşleştirmesi ve modifikasyonları yapılır.
        modified_scope = self._modify_scope(
            handler, scope, ParameterMappingTypes.RESPONSE
        )

        ret_response.headers = modified_scope.header
        ret_response.status_code = modified_scope.status_code
        ret_response.body = modified_scope.body

        return ret_response

    # Not : application/vnd.ogc.sld+xml ve application/vnd.ogc.se+xml parametreleri Harita servisinden SLD bilgilerini gateway üzerinden alırken uygulanıyor. (28.08.2023)
    # Not : application/vnd.mapbox-vector-tile parametresi Harita görüntülenmesi sırasındaki istekler için eklenmiştir.  (02.09.2023)
    # Not : application/vnd.ogc.wms_xml spatialBackend den external-wms istekleri için eklenmiştir.
    def transform_to_response(self, service_response: ServiceResponse) -> Response:
        """Handler ın ouşturduğu cevabı web response haline çevirir"""

        # Not : Harita katmanlarının output formatları. (07.09.2023)
        image_formats = [
            "image/gif",
            "image/jpeg",
            "image/png",
            "image/png8",
            "image/vnd.jpeg-png",
            "image/vnd.jpeg-png8",
            "image/png; mode=8bit",
            "application/octet-stream"
        ]

        params = {"content": service_response.body, "headers": service_response.headers, "status_code": service_response.status_code}
        if service_response.response_type.find("application/json") > -1:
            return JSONResponseX(**params)
        elif (
            service_response.response_type.find(
                "application/problem+json; charset=utf-8"
            )
            > -1
        ):
            return JSONResponseX(**params)
        elif (
            service_response.response_type.find("text/plain") > -1
            or service_response.response_type.find("text/xml") > -1
        ):
            return PlainTextResponse(**params)
        elif service_response.response_type.find("text/html") > -1:
            return HTMLResponse(**params)
        elif (
            service_response.response_type.find("application/gml+xml") > -1
            or service_response.response_type.find("application/xml") > -1
        ):
            return PlainTextResponse(**params)
        elif (
            service_response.response_type.find("application/vnd.ogc.sld+xml") > -1
            or service_response.response_type.find("application/vnd.ogc.se+xml") > -1
            or service_response.response_type.find("application/vnd.ogc.se_xml") > -1
        ):
            return PlainTextResponse(**params)
        elif (
            service_response.response_type.find("application/vnd.mapbox-vector-tile")
            > -1
        ):
            return PlainTextResponse(**params)
        elif service_response.response_type.find("application/vnd.ogc.wms_xml") > -1:
            return PlainTextResponse(**params)
        elif service_response.response_type in image_formats:
            return Response(
                params["content"], media_type=service_response.response_type
            )
        else:
            raise ValueError("ServiceResponseType not supported")

    def check_query_params(self, service_request: ServiceRequest, query: str) -> bool:
        """Gelen istekteki parametreler ile route da tanımlı olan parametreleri eşleştirir.
        parametre eksik olması durumunda False döner.
        ?param=val_1&param2=val_2 şeklinde tanımlanmış bir route.query değerinin kontrol edilmesi
        için request nesnesinde bulunan (path, query, body) değerlerinde param ve param2
        parametrelerinin olması gerekir.
        """
        params = {**service_request.path_params, **service_request.query_params}
        parsed_qs = parse_qs(urlparse(query).query)
        for param in parsed_qs:
            if not params.get(param, None):
                return False
        return True

    def _modify_scope(
        self, handler: IntegrationHandler, scope: ServiceScope, type: str
    ) -> ServiceScope:
        # Orjinal verinin kopyası alınır ve kopya üzerinde değişiklikler yapılır.
        copied = dict(scope)
        if handler.integration.parameter_mappings:
            for param_mapping in handler.integration.parameter_mappings:
                # Parametre eşleştirme listesi kopyalanan kapsam üzerinde uygulanır
                if param_mapping.type == type:
                    self._apply_params(copied, param_mapping.param_list or [])

        return ServiceScope(**copied)

    def _apply_params(
        self, scope: Dict[str, Any], param_list: List[RequestResponseMapping]
    ):
        # Parametreler scope objesi üzerinde uygulanır.
        for param in param_list:
            # parametre tipi ve değeri birleştirilir. Body ya da context parametre
            # tiplerinde içi içe kullanım sağlanabilir. body.a_obj.b_val gibi
            full_param = f"{param.parameter_type.lower()}.{param.parameter}"
            full_value = f"{param.value_type.lower()}.{param.value}"
            if param.value_type == ValueTypes.STATIC:
                full_value = param.value

            if param.modifier == ModifierTypes.REMOVE:
                self._rdelattr(scope, full_param)
            else:
                value = self._get_param_value(scope, full_value)
                self._rsetattr(scope, full_param, value)

    def _get_param_value(self, obj: Any, val_expr: str) -> Any:
        if val_expr.find(".") > -1:
            return self._rgetattr(obj, val_expr)
        else:
            return val_expr

    def _rsetattr(self, obj, attr, value):
        param_parts = attr.split(".")
        attr_path = ".".join(param_parts[:-1])
        attr = self._rgetattr(obj, attr_path)
        attr[param_parts[-1]] = value

    def _rgetattr(self, obj, attr):
        def _getattr(objx, attr):
            returnObj = objx.get(attr)
            if returnObj is None:
                returnObj = {}
                objx[attr] = returnObj
            return returnObj

        attr_list = attr.split(".")
        if len(attr_list) > 1:
            return reduce(_getattr, attr.split("."), obj)
        else:
            return obj[attr]

    def _rdelattr(self, obj, attr):
        attr_list = attr.split(".")
        attr_list2 = attr_list[:-1]
        attr2: Any = self._rgetattr(obj, (".").join(attr_list2))
        if attr2:
            del attr2[attr_list[-1]]

    def _create_routes(self, routes: List[Route]) -> List[Tuple[Route, APIRoute]]:
        route_tuples: List[Tuple[Route, APIRoute]] = []
        for route in routes or []:
            api_route = APIRoute(
                route.path,
                dummy_endpoint_func,
                methods=(
                    [route.method_type]
                    if route.method_type != MethodTypes.ANY
                    else ALL_METHODS
                ),
            )
            route_tuples.append((route, api_route))
        return route_tuples

    def _create_handler_model(
        self, route: Route, api_route: APIRoute, path_params: Any
    ) -> IntegrationHandler | None:
        if not route.integration:
            raise ValueError(f"{route.integration_id} integration not found")

        params = (route, path_params)
        match route.integration.type:
            case IntegrationTypes.HTTP_BACKEND:
                return HttpIntegrationHandler(*params)
            case IntegrationTypes.ADHOC_QUERY:
                # if (route
                #         and route.integration
                #         and route.integration.connection_info
                #         and route.integration.connection_info.params
                #         and route.integration.connection_info.params.get('dialect') == 'postgresql'):
                #     return AsyncAdHocQueryIntegrationHandler(*params)
                # else:
                return AdHocQueryIntegrationHandler(*params)
            case IntegrationTypes.SOAP_BACKEND:
                return SoapIntegrationHandler(*params)
            case IntegrationTypes.SPATIAL_BACKEND:
                return SpatialIntegrationHandler(*params)
            case IntegrationTypes.ELASTIC_BACKEND:
                return ElasticIntegrationHandler(*params)
            case IntegrationTypes.MONGO_QUERY:
                return MongoIntegrationHandler(*params)
        return None
