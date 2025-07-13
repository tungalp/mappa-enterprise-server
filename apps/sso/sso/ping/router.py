from fastapi import APIRouter
from dependency_injector.wiring import inject
from datetime import datetime

router = APIRouter()

@router.get("/")
@inject
async def ping():
    print(datetime.now())
    return {
        "ping": "pong",
    }
