from sqlalchemy import Column, Text, UniqueConstraint, JSON, Boolean
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
import uuid
from sqlalchemy.sql import func
import uuid
from mapa.manage.constants import LdapAuthenticationOptions, LdapAutoBindOptions, LdapGetInfoOptions

class LdapServerEntity(EntityMixin, Base):
    """Ldap Db Model"""

    __tablename__ = "ldap_server"  # type: ignore
    __table_args__ = {"schema": "manage"}

    name = Column(Text, nullable=False, index=True)  
    url = Column(Text, nullable=False) 
    username = Column(Text, nullable=False)   
    password = Column(Text, nullable=False) 
    search_base = Column(Text, nullable=False) 
    search_filter = Column(Text, nullable=False) 

    get_info = Column(
        Text, nullable=False, default=LdapGetInfoOptions.ALL
    )  
    authentication = Column(
        Text, nullable=False, default=LdapAuthenticationOptions.SIMPLE
    )  
    auto_bind = Column(
        Text, nullable=False, default=LdapAutoBindOptions.DEFAULT
    )  
    attribute_map = Column(JSON, nullable=False)  
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)  # Tenant ID
    UniqueConstraint(name, tenant_id, name="ldap_uk_1")
