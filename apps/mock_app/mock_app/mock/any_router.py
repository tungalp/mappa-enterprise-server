import json
from typing import List
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


router = APIRouter()
ALL_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

# @router.get("/")
# @router.post("/")
# @router.put("/")
# @router.delete("/")
# @router.patch("/")
# @router.head("/")
# @router.options("/")
@router.api_route("/", methods=ALL_METHODS)
async def any_method(
    request: Request
):
    return JSONResponse(content=jsonable_encoder({
        "method": request.method
    }))