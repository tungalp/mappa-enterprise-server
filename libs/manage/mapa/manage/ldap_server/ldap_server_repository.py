from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.ldap_server.ldap_server_entity import LdapServerEntity


class LdapServerRepository(BaseRepository[LdapServerEntity]):
    """LdapServer Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, LdapServerEntity)
