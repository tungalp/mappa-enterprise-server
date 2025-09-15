import asyncio
import time
import logging
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

# Configure performance logger
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)

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
    # Start overall timing
    start_time = time.perf_counter()
    timing_data = {}

    try:
        # Tenant lookup timing
        tenant_start = time.perf_counter()
        tenant_id = await root_service.find_tenant_id(tenant_name)
        timing_data['tenant_lookup'] = time.perf_counter() - tenant_start

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant not found"
            )

        # API lookup timing
        api_lookup_start = time.perf_counter()
        api = await root_service.find_api(str(tenant_id), api_path)
        timing_data['api_lookup'] = time.perf_counter() - api_lookup_start

        if not api:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Api not found"
            )

        # API details lookup timing
        api_details_start = time.perf_counter()
        api = await root_service.get_api_with_details(str(tenant_id), api.id)
        timing_data['api_details_lookup'] = time.perf_counter() - api_details_start

        # Handler finding timing
        handler_start = time.perf_counter()
        handler = root_service.find_handler(api, route_path, request.method)
        timing_data['handler_lookup'] = time.perf_counter() - handler_start

        if not handler:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Route not found"
            )

        # Rate limiting timing
        rate_limit_start = time.perf_counter()
        request_count = 0
        if handler.route.rate_limit is not None:
            client_ip = request.client.host  # type: ignore
            redis: Redis = FastAPICache.get_backend().redis
            key = f"rate_limit:{client_ip}"
            request_count = await redis.get(key)
            request_count = int(request_count or 0)
            if request_count and int(request_count) >= handler.route.rate_limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
        timing_data['rate_limiting'] = time.perf_counter() - rate_limit_start

        # Authentication and authorization timing
        auth_start = time.perf_counter()
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
        timing_data['authentication'] = time.perf_counter() - auth_start

        # Context preparation timing
        context_start = time.perf_counter()
        tenant_context = await root_service.find_context_var(str(tenant_id))
        context = {
            **tenant_context,
            **(api.context or {}),
            **(handler.integration.context or {}),
        }
        timing_data['context_preparation'] = time.perf_counter() - context_start

        # Service request creation timing
        request_creation_start = time.perf_counter()
        service_request = await root_service.create_service_request(
            request, handler, {"path": route_path, "context": context}
        )
        timing_data['service_request_creation'] = time.perf_counter() - request_creation_start

        # Request modification timing
        request_mod_start = time.perf_counter()
        modified_request = root_service.modify_service_request(service_request, handler)
        timing_data['request_modification'] = time.perf_counter() - request_mod_start

        # Request logging preparation timing
        logging_prep_start = time.perf_counter()
        if handler.route.full_logging == True:
            try:
                request_body_str = json.dumps(service_request.body, ensure_ascii=False, cls=JsonEncoder)
            except Exception:
                request_body_str = "parse_error"
        timing_data['logging_preparation'] = time.perf_counter() - logging_prep_start

        # Query parameter validation timing
        query_validation_start = time.perf_counter()
        if not root_service.check_query_params(
            modified_request, handler.route.query or ""
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str("Required query params not found"),
            )
        timing_data['query_validation'] = time.perf_counter() - query_validation_start

        # Handler execution timing (most critical part)
        execution_start = time.perf_counter()
        service_response: ServiceResponse = await retry_logic(lambda: handler.execute(modified_request), handler.route.retry_count if handler.route.retry_count else 1, handler.route.retry_millisecond, lambda: fallback_response())  # type: ignore
        # service_response = await handler.execute(modified_request)
        timing_data['handler_execution'] = time.perf_counter() - execution_start

        service_response.context = service_request.context
        # Response logging preparation timing
        response_logging_start = time.perf_counter()
        if handler.route.full_logging == True:
            try:
                response_body_str = json.dumps(
                    service_response.body, ensure_ascii=False, cls=JsonEncoder
                )
            except Exception:
                response_body_str = "parse_error"
        timing_data['response_logging_prep'] = time.perf_counter() - response_logging_start

        # Response modification timing
        response_mod_start = time.perf_counter()
        modified_response = root_service.modify_service_response(
            service_response, handler
        )
        timing_data['response_modification'] = time.perf_counter() - response_mod_start

        # Header and rate limit processing timing
        header_processing_start = time.perf_counter()
        modified_response.headers["X-Cache-Second"] = str(handler.route.cache_timeout)

        if (
            handler.route.rate_limit is not None
            and handler.route.rate_second is not None
        ):
            modified_response.headers["X-Rate-Limit"] = str(int(request_count) + 1)
            await redis.incr(key)
            await redis.expire(key, handler.route.rate_second)
        timing_data['header_processing'] = time.perf_counter() - header_processing_start

        # APM and logging timing
        apm_logging_start = time.perf_counter()
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
        timing_data['apm_logging'] = time.perf_counter() - apm_logging_start

        # Response transformation timing
        transform_start = time.perf_counter()
        ret_res = root_service.transform_to_response(modified_response)
        timing_data['response_transformation'] = time.perf_counter() - transform_start

        # Calculate total time and log performance data
        total_time = time.perf_counter() - start_time
        timing_data['total_time'] = total_time

        # Log detailed performance metrics
        request_info = f"{request.method} {tenant_name}/{api_path}/{route_path}"
        log_detailed_performance(timing_data, request_info)

        # Add timing data to response headers for debugging
        ret_res.headers["X-Timing-Total"] = format_timing_ms(total_time)
        ret_res.headers["X-Timing-Execute"] = format_timing_ms(timing_data['handler_execution'])
        ret_res.headers["X-Timing-Breakdown"] = json.dumps({
            k: format_timing_ms(v) for k, v in timing_data.items()
        })

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
    retry_start = time.perf_counter()

    while max_retries is None or attempts < max_retries:
        try:
            attempt_start = time.perf_counter()
            result = await func()
            attempt_time = time.perf_counter() - attempt_start
            total_retry_time = time.perf_counter() - retry_start

            # Log retry performance if there were multiple attempts
            if attempts > 0:
                perf_logger.info(
                    f"Retry successful after {attempts + 1} attempts. "
                    f"Last attempt: {attempt_time*1000:.2f}ms, "
                    f"Total retry time: {total_retry_time*1000:.2f}ms"
                )

            return result

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


def format_timing_ms(seconds: float) -> str:
    """Format timing in milliseconds with 2 decimal places"""
    return f"{seconds * 1000:.2f}ms"


def log_detailed_performance(timing_data: dict, request_info: str):
    """Log detailed performance breakdown"""
    total_time = timing_data.get('total_time', 0)

    # Calculate percentages
    percentages = {}
    for key, value in timing_data.items():
        if key != 'total_time' and total_time > 0:
            percentages[key] = (value / total_time) * 100

    # Create detailed log message
    details = []
    for key, value in timing_data.items():
        if key != 'total_time':
            percentage = percentages.get(key, 0)
            details.append(f"{key}: {format_timing_ms(value)} ({percentage:.1f}%)")

    perf_logger.info(
        f"PERFORMANCE BREAKDOWN for {request_info} | "
        f"TOTAL: {format_timing_ms(total_time)} | "
        f"{' | '.join(details)}"
    )
