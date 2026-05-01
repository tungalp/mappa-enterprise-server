from fastapi import Request
from fastapi.responses import JSONResponse
from messaging.app import create_application
from sqlalchemy import exc as sa_exc
import re

app = create_application()

@app.exception_handler(sa_exc.IntegrityError)
async def integrity_error_handling(request: Request, exc: sa_exc.IntegrityError):
    try:
        error_message = re.findall(r'["][\w\s]+["]', exc.args[0])[0].replace('"', "")
    except Exception:
        error_message = "Veri bütünlüğü ihlali"

    return JSONResponse(status_code=512, content=str(error_message))

@app.exception_handler(sa_exc.DBAPIError)
async def raise_error_handling(request: Request, exc: sa_exc.DBAPIError):
    try:
        error_message = str(exc.orig.diag.message_primary) # type: ignore
    except Exception:
        error_message = "Veritabanı hatası"

    return JSONResponse(status_code=512, content=str(error_message))

@app.get("/health")
def health_check():
    return {"status": "ok"}
