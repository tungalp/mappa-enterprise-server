import json
from typing import List
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


router = APIRouter()


class Parsel(BaseModel):
    id: int
    ada_no: str
    parsel_no: str
    alan: float
    
data = [
    Parsel(id=1, ada_no="100", parsel_no="1", alan=1200),
    Parsel(id=2, ada_no="100", parsel_no="2", alan=1250),
    Parsel(id=3, ada_no="100", parsel_no="3", alan=1300),
    Parsel(id=4, ada_no="100", parsel_no="4", alan=1350)
]    

@router.get("/list")
async def list_parsel(
    request: Request
):
    ada_no = request.query_params.get("ada_no") or "ABC"
    parsel_no = request.query_params.get("parsel_no") or "ABC"
    
    filtered_data = list(filter(lambda x: x.ada_no == ada_no and x.parsel_no == parsel_no, data))
    return JSONResponse(content=jsonable_encoder(filtered_data))


@router.get("/{parsel_id}")
async def get_parsel(
    request: Request,
    parsel_id: int
):
    parsel = next(filter(lambda x: x.id == parsel_id, data), None)
    if parsel:
        return JSONResponse(content=jsonable_encoder(parsel))
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/")
async def post_parsel(
    request: Request
):
    try:
        body = await request.body()
        return JSONResponse(content={
            "affected": 1,
            "data": body.decode("utf-8")
        })
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)) from ex


@router.put("/{parsel_id}")
async def put(
    request: Request,
    parsel_id: int
):
    try:
        body = await request.body()
        return JSONResponse(content={
            "affected": 1,
            "data": body
        })
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)) from ex


@router.delete("/{parsel_id}")
async def delete(
    request: Request,
    parsel_id: int
):
    try:
        return JSONResponse(content={
            "affected": 1
        })
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)) from ex
