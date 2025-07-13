from typing import Optional
from pydantic import BaseModel


class NewPasswordEndpoint(BaseModel):
    """"Yeni şifre"""
    client_id: str
    password: str
    token: str
