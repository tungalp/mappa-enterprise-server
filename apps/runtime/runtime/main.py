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