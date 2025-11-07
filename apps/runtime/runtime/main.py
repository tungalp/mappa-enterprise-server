from fastapi import Request
from fastapi.responses import JSONResponse
from runtime.app import create_application
from sqlalchemy import exc
import re

app = create_application()

@app.exception_handler(exc.IntegrityError)
async def integrity_error_handling(request: Request, exc: exc.IntegrityError):
    return JSONResponse(status_code=512, content=str(re.findall(r'["][\w\s]+["]', exc.args[0])[0].replace('"', "")))

@app.exception_handler(exc.DBAPIError)
async def raise_error_handling(request: Request, exc: exc.DBAPIError):
    return JSONResponse(status_code=512, content=str(exc.args[0].split(':')[1].strip()))


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