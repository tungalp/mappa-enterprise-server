from fastapi import Request
from fastapi.responses import JSONResponse
from gateway.app import create_application
from sqlalchemy import exc as sa_exc
import re
from elasticapm import get_trace_id

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

@app.exception_handler(ValueError)
async def raise_value_error_handling(request: Request, exc: ValueError):
    trace_id = get_trace_id()
    request.app.apm_client.capture_exception()

    error_message = str(exc.args[0]) if exc.args else "Geçersiz değer"

    response = JSONResponse(status_code=512, content=error_message)
    response.headers["X-Trace-Id"] = trace_id or "unknown"
    return response


@app.get("/")
async def root():
    """Root function

    Returns:
        Object: Dönüş mesajı
    """
    return {
        "msg": "Hello from Gateway"
    }


@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"})