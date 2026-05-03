from mapa.core.data.base_entity import Base, EntityMixin
from sqlalchemy import Column, UniqueConstraint, DateTime, String
from sqlalchemy_utils import UUIDType


class FileStoreEntity(EntityMixin, Base):
    """FileStore Db Model"""

    __tablename__ = "file_store"  # type: ignore

    __table_args__ = {'schema': 'spatial'}

    creator_user_id = Column(UUIDType(binary=False), index=False, nullable=True)
    updater_user_id = Column(UUIDType(binary=False), index=False, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    file_format = Column(String(5), nullable=False)
    file_url = Column(String, nullable=True)


    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(file_url, tenant_id, name='spatial_file_store_uk_1')

