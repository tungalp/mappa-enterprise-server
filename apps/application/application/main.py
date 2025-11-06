from fastapi import Request
from fastapi.responses import JSONResponse
from application.app import create_application
from sqlalchemy import exc
import re
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError
from elasticapm import get_trace_id
from sqlalchemy import exc as sa_exc

app = create_application()


@app.exception_handler(Exception)
async def universal_handler(request: Request, exc: Exception):
    trace_id = get_trace_id()
    request.app.apm_client.capture_exception()

    status_code = 500
    content = str(exc)

    if isinstance(exc, sa_exc.IntegrityError):
        status_code = 512
        try:
            content = str(re.findall(r'["][\w\s]+["]', exc.args[0])[0].replace('"', ""))
        except Exception:
            content = "Veri bütünlüğü ihlali"

    elif isinstance(exc, sa_exc.DBAPIError):
        status_code = 512
        try:
            content = str(exc.orig.diag.message_primary)  # type: ignore
        except Exception:
            try:
                content = str(exc.args[0].raw_msg.split("\n")[0])
            except Exception:
                content = "Veritabanı hatası"

    response = JSONResponse(status_code=status_code, content=content)
    response.headers["X-Trace-Id"] = trace_id or "unknown"
    return response

@app.exception_handler(sa_exc.IntegrityError)
async def integrity_error_handling(request: Request, exc: sa_exc.IntegrityError):
    trace_id = get_trace_id()
    request.app.apm_client.capture_exception()

    try:
        error_message = re.findall(r'["][\w\s]+["]', exc.args[0])[0].replace('"', "")
    except Exception:
        error_message = "Veri bütünlüğü ihlali"

    response = JSONResponse(
        status_code=512,
        content= str(error_message),
    )
    response.headers["X-Trace-Id"] = trace_id or "unknown"
    return response

@app.exception_handler(sa_exc.DBAPIError)
async def raise_error_handling(request: Request, exc: sa_exc.DBAPIError):
    trace_id = get_trace_id()
    request.app.apm_client.capture_exception()

    try:
        error_message = str(exc.orig.diag.message_primary)  # type: ignore
    except Exception:
        try:
            error_message = exc.args[0].raw_msg.split("\n")[0]
        except Exception:
            error_message = "Veritabanı hatası"

    response = JSONResponse(
        status_code=512,
        content= str(error_message),
    )
    response.headers["X-Trace-Id"] = trace_id or "unknown"
    return response


@app.get("/")
async def root():
    """Root function

    Returns:
        Object: Dönüş mesajı
    """
    return {"msg": "Hello from Application"}


@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"})


@app.get("/ready")
async def readiness_check(request: Request):
    """Readiness check - service is ready to handle requests"""
    # Check Redis connectivity if available
    try:
        if hasattr(request.app.state, "redis_write") and hasattr(request.app.state, "redis_read"):
            await request.app.state.redis_write.ping()
            await request.app.state.redis_read.ping()
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": f"redis_error: {str(e)}"}
        )

    return JSONResponse(content={"status": "ready"})
