from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel

from mapa.gateway.constant import AuthenticationInfoTypes


class BasicAuthAuthenticationInfo(BaseModel):
    """BasicAuth Type Modeli"""
    username: str
    password: str


class ApiKeyAuthenticationInfo(BaseModel):
    """ApiKey Type Modeli"""
    key: str
    value: str
    add_to: str


class BearerTokenAuthenticationInfo(BaseModel):
    """BearerToken Type Modeli"""
    token: str


class AuthenticationInfo(BaseModel):
    """AuthenticationInfo Modeli"""
    type: str = AuthenticationInfoTypes.BASICAUTH
    auth_params: BasicAuthAuthenticationInfo | ApiKeyAuthenticationInfo | BearerTokenAuthenticationInfo


class CreateAuthenticationInfo(BaseModel):
    type: str
    auth_params: BasicAuthAuthenticationInfo | ApiKeyAuthenticationInfo | BearerTokenAuthenticationInfo


class UpdateAuthenticationInfo(BaseModel):
    type: str | None = None
    auth_params: BasicAuthAuthenticationInfo | ApiKeyAuthenticationInfo | BearerTokenAuthenticationInfo | None = None


class UpdateAllAuthenticationInfo(BaseModel):
    type: str | None = None
    auth_params: BasicAuthAuthenticationInfo | ApiKeyAuthenticationInfo | BearerTokenAuthenticationInfo | None = None
