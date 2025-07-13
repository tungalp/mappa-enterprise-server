from typing import  Optional
from uuid import UUID
from pydantic import BaseModel


class ProfileAdaptor(BaseModel):
    """ProfileAdaptor Modeli"""
    id: UUID
    user_info_endpoint: str
    user_info_list_endpoint:str

class CreateProfileAdaptor(BaseModel):
    user_info_endpoint: str
    user_info_list_endpoint:str | None = None

class UpdateProfileAdaptor(BaseModel):
    user_info_endpoint: str
    user_info_list_endpoint:str | None = None

class UpdateAllProfileAdaptor(UpdateProfileAdaptor):
    pass
    