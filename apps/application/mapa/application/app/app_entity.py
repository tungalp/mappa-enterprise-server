from sqlalchemy import Column, Text, UniqueConstraint, JSON, Numeric
from mapa.core.data.base_entity import Base, EntityMixin
from nanoid import generate
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship


class AppEntity(EntityMixin, Base):
    """App Db Model"""

    __tablename__ = "app"  # type: ignore

    __table_args__ = {'schema': 'application'}

    name = Column(Text, nullable=False)
    code = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    logo = Column(Text, nullable=True)
    menu = Column(JSON, nullable=True, default=[])
    translation = Column(JSON, nullable=True, default={'en': {}, 'tr': {}})
    client_id = Column(Text, nullable=False, index=True)
    api_id = Column(UUIDType(binary=False), nullable=False, index=True)
    logout_uri = Column(Text, nullable=True)
    return_uri = Column(Text, nullable=True)
    client_secret = Column(Text, nullable=False)
    identifier = Column(Text, nullable=False)
    ordr = Column(Numeric, nullable=False)
    content_page = relationship(
        "ContentPageEntity", back_populates="app", cascade="all, delete-orphan")

    # TODO: TenantMixin base classından kullanıldığı zaman unique constraint verilmediği için class'a yazıldı. 05.03.2023
    tenant_id = Column(UUIDType(binary=False), index=True, nullable=False)
    UniqueConstraint(name, tenant_id, name='app_uk_1')
