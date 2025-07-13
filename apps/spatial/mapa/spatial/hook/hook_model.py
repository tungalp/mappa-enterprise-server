from uuid import UUID

from mapa.spatial.constant import HookOperationType, HookType
from pydantic import BaseModel


class Hook(BaseModel):
    """Hook Modeli"""

    id: UUID
    type: HookType
    operation_type: HookOperationType
    description: str | None = None


class CreateHook(BaseModel):
    type: HookType
    operation_type: HookOperationType
    description: str | None = None


class UpdateHook(BaseModel):
    type: HookType
    operation_type: HookOperationType
    description: str | None = None


class UpdateAllHook(BaseModel):
    description: str | None = None
