import uuid
from sqlalchemy import Column, DateTime, text, event, Uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, declared_attr, declarative_mixin


NULL_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")


class Base(DeclarativeBase):
    ...

@declarative_mixin
class EntityMixin(object):
    """Veritabanı entity sınıfları yardımcı sınıf
    Yeni bir entity oluştururken EntityMixin ve Base beraber kullanılırlar
    class BuildingEntity(EntityMixin, Base):
        __tablename__ = "building"
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Uuid(), primary_key=True, default=uuid.uuid4, insert_sentinel=True)

    created_at = Column(DateTime, default=func.now())


@declarative_mixin
class TenantMixin(object):
    """Tenant bazlı tablolar için kullanılacak olan sınıftır. Veriler tenant_id
    ile sınıflandırılırlar
    ParcelEntity(EntityMixin, TenantMixin, Base):
        __tablename__ = "parcel"
    """

    tenant_id = Column(Uuid(), index=True, nullable=True)


@event.listens_for(Base.metadata, 'after_create')
def receive_after_create(target, connection, tables, **kw):
    """tenant_id alanı bulunan tablolar için bir policy oluşturur. Bu durumda select,
    insert, update işlemleri için mutlaka app.tenant_id set edilmesi gerekir.
    """
    tenant_tables = [
        table for table in tables for col in table.columns if col.name == "tenant_id"
    ]
    for tenant_table in tenant_tables:
        connection.execute(
            text(f"alter table {tenant_table.fullname} enable row level security"))
        connection.execute(text(
            f"create policy {tenant_table.name}_isolation_policy on {tenant_table.fullname} "
            f"using  ( (current_setting('app.tenant_id') = tenant_id::text) OR ((tenant_id)::text = '{str(NULL_TENANT_ID)}') )"
        ))
