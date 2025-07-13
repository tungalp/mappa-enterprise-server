from typing import Any, Dict, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel
from mapa.app.params import fields_param
from mapa.sso.models import User, CreateUser
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from sso.config.app_container import AppContainer
from fastapi.responses import JSONResponse

router = APIRouter()


class Message(BaseModel):
    message: str


@router.get("/{user_id}", response_model=User)
@inject
async def get(
    request: Request,
    user_id: UUID,
    field_list: List[str | Dict[str, Any]] = fields_param(),
    messenger: ServiceMessenger = Depends(
        Provide[AppContainer.user_package.messenger]
    ),
):
    tenant_id = request.user.tenant_id
    user = await messenger.get_by_user_id(str(user_id), field_list, tenant_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("Item Not Found")
        )

    return user


@router.post("/", response_model=User)
@inject
async def create(
    request: Request,
    create_input: CreateUser,
    messenger: ServiceMessenger = Depends(
        Provide[AppContainer.user_package.messenger]
    ),
):
    tenant_id = request.user.tenant_id
    user = await messenger.create_user(create_input.model_dump(), tenant_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("Item Not Found")
        )

    return user
