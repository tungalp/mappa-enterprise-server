from fastapi import Request
from fastapi.responses import JSONResponse
from mock_app.app import create_application


app = create_application()


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
