from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel
from mapa.manage.constants import (
    LdapAuthenticationOptions,
    LdapAutoBindOptions,
    LdapGetInfoOptions,
)


class LdapServer(BaseModel):
    """LDAP Sunucu Modeli"""

    id: UUID
    name: str
    url: str
    username: str
    password: Optional[str] = None
    get_info: str
    authentication: str
    auto_bind: str
    attribute_map: Dict[str, list[str]]
    search_base: str
    search_filter: str


class CreateLdapServer(BaseModel):
    """LDAP Sunucu Oluşturma Modeli"""

    name: str
    url: str
    username: str
    password: str
    get_info: str = LdapGetInfoOptions.ALL
    authentication: str = LdapAuthenticationOptions.SIMPLE
    auto_bind: str = LdapAutoBindOptions.DEFAULT
    attribute_map: Dict[str, list[str]]
    search_base: str
    search_filter: str


class UpdateLdapServer(BaseModel):
    """LDAP Sunucu Güncelleme Modeli"""

    name: Optional[str] = None
    url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    get_info: Optional[str] = None
    authentication: Optional[str] = None
    auto_bind: Optional[str] = None
    attribute_map: Optional[Dict[str, list[str]]] = None
    search_base: Optional[str] = None
    search_filter: Optional[str] = None


class UpdateAllLdapServer(UpdateLdapServer):
    """LDAP Tüm Alanları Güncelleme Modeli"""

    pass


class LdapUser(BaseModel):
    """ "LdapUser parametreleri"""

    name: str
    middlename: str
    surname: str
    email: str
    password: str
    phone: str | None = None
    is_active: bool | None = None
    ldap_user_id: UUID | None = None
