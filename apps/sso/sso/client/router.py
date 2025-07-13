from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from dependency_injector.wiring import Provide, inject
from mapa.sso.models import ClientInfo
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from sso.config.app_container import AppContainer

router = APIRouter()
@router.get("/info/{client_id}", response_model=ClientInfo)
@inject
async def get_info(
    request: Request,
    client_id: str,
    messenger: ServiceMessenger = Depends(
        Provide[AppContainer.client_package.messenger])):
    """Genel Client bilgilerini getirir"""
    client_info = await messenger.get_client_info(client_id)
    if not client_info: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str('Item Not Found'))
    return client_info