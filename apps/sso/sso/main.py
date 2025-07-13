from fastapi import Request
from fastapi.responses import JSONResponse
from sso.app import create_application
from elasticapm import get_trace_id
from sqlalchemy import exc as sa_exc
import re

app = create_application()

@app.exception_handler(Exception)
async def universal_handler(request: Request, exc: Exception):
    trace_id = get_trace_id()
    request.app.apm_client.capture_exception()

    content = str(exc)
    status_code = 500

    if "IntegrityError" in str(exc):
        status_code = 512
        try:
            content = str(re.findall(r'["][\w\s]+["]', exc.args[0])[0].replace('"', ""))
        except:
            content = "Veri bütünlüğü hatası"

    elif "DBAPIError" in str(exc):
        status_code = 512
        try:
            content = exc.args[0].split(":")[1].strip()
        except:
            content = "Veritabanı erişim hatası"

    response = JSONResponse(status_code=status_code, content=content)
    response.headers["X-Trace-Id"] = trace_id or "unknown"
    return response


@app.exception_handler(sa_exc.IntegrityError)
async def integrity_error_handling(request: Request, exc: sa_exc.IntegrityError):
    trace_id = get_trace_id()
    request.app.apm_client.capture_exception()

    try:
        error_message = re.findall(r'["][\w\s]+["]', exc.args[0])[0].replace('"', "")
    except:
        error_message = "Veri bütünlüğü hatası"

    response = JSONResponse(status_code=512, content=error_message)
    response.headers["X-Trace-Id"] = trace_id or "unknown"
    return response


@app.exception_handler(sa_exc.DBAPIError)
async def raise_error_handling(request: Request, exc: sa_exc.DBAPIError):
    trace_id = get_trace_id()
    request.app.apm_client.capture_exception()

    try:
        error_message = exc.args[0].split(":")[1].strip()
    except:
        error_message = "Veritabanı erişim hatası"

    response = JSONResponse(status_code=512, content=error_message)
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


@app.exception_handler(NameError)
async def raise_name_error_handling(request: Request, exc: NameError):
    trace_id = get_trace_id()
    request.app.apm_client.capture_exception()

    error_message = str(exc.args[0]) if exc.args else "Tanımsız isim hatası"

    response = JSONResponse(status_code=409, content=error_message)
    response.headers["X-Trace-Id"] = trace_id or "unknown"
    return response


@app.get("/")
async def root():
    """Root function

    Returns:
        Object: Dönüş mesajı
    """
    return {
        "msg": "Hello from SSO"
    }


@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"})