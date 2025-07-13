import asyncio
import time
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide
from fastapi_cache import FastAPICache
from redis import Redis
from mapa.core.data.exceptions import FallbackTriggeredException
from mapa.core.data.json_encoder import JsonEncoder
from mapa.security import authorize
from service.config.app_container import AppContainer
from sqlalchemy import exc
from service.model.response import ServiceResponse
from service.root.root_service import RootService
import json
import hashlib
import sqlalchemy.exc
import elasticapm

router = APIRouter()

ALL_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

NO_FALLBACK_STATUS_CODES = {400, 401, 403, 404, 422, 500}
SQLA_EXCEPTIONS = sqlalchemy.exc.SQLAlchemyError


# @router.get("/{tenant_name:str}/{api_path:str}/{route_path:path}")
# @router.post("/{tenant_name:str}/{api_path:str}/{route_path:path}")
# @router.put("/{tenant_name:str}/{api_path:str}/{route_path:path}")
# @router.delete("/{tenant_name:str}/{api_path:str}/{route_path:path}")
@router.api_route(
    "/{tenant_name:str}/{api_path:str}/{route_path:path}", methods=ALL_METHODS
)
@inject
async def root(
    request: Request,
    tenant_name: str,
    api_path: str,
    route_path: str,
    root_service: RootService = Depends(
        Provide[AppContainer.root_package.root_service]
    ),
):
    """Root Method"""
    try:
        # Tenant
        tenant_id = await root_service.find_tenant_id(tenant_name)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant not found"
            )
        # Api_path değeriyle eşleşen api kaydı bulunur.
        api = await root_service.find_api(str(tenant_id), api_path)
        if not api:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Api not found"
            )

        # İlgili api detay bilgileri ile beraber sorgulanır.
        api = await root_service.get_api_with_details(str(tenant_id), api.id)

        # IntegrationHandler
        handler = root_service.find_handler(api, route_path, request.method)
        if not handler:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
            )

        request_count = 0
        if handler.route.rate_limit is not None:
            client_ip = request.client.host  # type: ignore
            redis: Redis = FastAPICache.get_backend().redis
            key = f"rate_limit:{client_ip}"
            request_count = await redis.get(key)
            request_count = int(request_count or 0)
            if request_count and int(request_count) >= handler.route.rate_limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Scope ve tenant kontrolü yapılır
        if handler.route.scope:
            if not request.user.is_authenticated:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated",
                )
            # İstenen yetki token da tanımlı olmalıdır
            if not (request.auth and handler.route.scope in request.auth.scopes):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unsupported scope"
                )
            # Token daki tenant ile istek bulunan aynı tenant olmalıdır.
            if str(tenant_id) != str(request.user.payload.get("tenant_id")):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tenant_ids are different",
                )

        tenant_context = await root_service.find_context_var(str(tenant_id))
        context = {
            **tenant_context,
            **(api.context or {}),
            **(handler.integration.context or {}),
        }
        # Service Request oluşturulur
        service_request = await root_service.create_service_request(
            request, handler, {"path": route_path, "context": context}
        )

        # Request parametre eşleşmesine göre düzenlenir.
        modified_request = root_service.modify_service_request(service_request, handler)

        if handler.route.full_logging == True:
            try:
                request_body_str = json.dumps(service_request.body, ensure_ascii=False, cls=JsonEncoder)
            except Exception:
                request_body_str = "parse_error"

        # Route da tanımlanmış olan query parametrelerinin kontrolü yapılır.
        # Eğer query de tanımlı olan herhangi bir parametrede (path, query, body, context) geçmiyorsa hata verir
        if not root_service.check_query_params(
            modified_request, handler.route.query or ""
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str("Required query params not found"),
            )

        # retry_logic fonksiyonu ile retry işlemi yapılır. config'den alınan değerlerle retry mantığı oluşturulabilir.
        service_response: ServiceResponse = await retry_logic(lambda: handler.execute(modified_request), handler.route.retry_count if handler.route.retry_count else 1, handler.route.retry_millisecond, lambda: fallback_response())  # type: ignore
        # service_response = await handler.execute(modified_request)
        service_response.context = service_request.context
        if handler.route.full_logging == True:
            try:
                response_body_str = json.dumps(
                    service_response.body, ensure_ascii=False, cls=JsonEncoder
                )
            except Exception:
                response_body_str = "parse_error"

        # Dönüş değeri parametre eşleşmesine göre düzenlenir.
        modified_response = root_service.modify_service_response(
            service_response, handler
        )

        modified_response.headers["X-Cache-Second"] = str(handler.route.cache_timeout)

        if (
            handler.route.rate_limit is not None
            and handler.route.rate_second is not None
        ):
            modified_response.headers["X-Rate-Limit"] = str(int(request_count) + 1)
            await redis.incr(key)
            await redis.expire(key, handler.route.rate_second)

        # Handler dan gelen değer Web Response nesnesine dönüştürülür.

        if handler.route.full_logging == True:
            elasticapm.set_custom_context(  # type: ignore
                {
                    "req_body": safe_truncate(request_body_str),
                    "resp_body": safe_truncate(response_body_str),
                }
            )
            
        user = getattr(request, "user", None)
        if user and getattr(user, "sub", None):
            elasticapm.set_user_context(user_id=user.sub)  # type: ignore

        ret_res = root_service.transform_to_response(modified_response)
        return ret_res

    except HTTPException as ex:
        raise ex
    except exc.DBAPIError as ex:
        raise ex
    except FallbackTriggeredException as ex:
        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(repr(ex))
        ) from ex


async def fallback_response():
    raise FallbackTriggeredException(
        "Service temporarily unavailable, fallback triggered"
    )


async def retry_logic(func, max_retries=1, wait_time_ms=1000, fallback_func=None):
    attempts = 0
    last_exception = None

    while max_retries is None or attempts < max_retries:
        try:
            return await func()

        except HTTPException as http_exc:
            last_exception = http_exc

        except SQLA_EXCEPTIONS as db_exc:
            last_exception = db_exc

        except Exception as e:
            last_exception = e

        attempts += 1
        if wait_time_ms:
            await asyncio.sleep(wait_time_ms / 1000)

    if isinstance(last_exception, SQLA_EXCEPTIONS):
        raise last_exception

    if (
        isinstance(last_exception, HTTPException)
        and last_exception.status_code in NO_FALLBACK_STATUS_CODES
    ):
        raise last_exception

    if fallback_func:
        return await fallback_func()

    raise HTTPException(
        status_code=500,
        detail=f"Failed after {attempts} retries: {str(last_exception)}",
    )


def safe_truncate(value: str, max_len: int = 10000) -> str:
    try:
        return value[:max_len]
    except Exception:
        return "[TRUNCATE_ERROR]"
