from fastapi import APIRouter
from dependency_injector.wiring import inject

router = APIRouter()

@router.get("/")
@inject
async def ping():
    return {
        "ping": "pong"
    }
