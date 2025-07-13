from sqlalchemy import Column, Text, DateTime, ForeignKey
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from sqlalchemy_utils import UUIDType


class ProfileAdaptorEntity(EntityMixin, TenantMixin, Base):
    """ProfileAdaptor Db Model"""

    __tablename__ = "profile_adaptor"  # type: ignore
    __table_args__ = {'schema': 'manage'}
    
    user_info_endpoint = Column(Text, nullable=False)
    user_info_list_endpoint = Column(Text, nullable=True)
    
