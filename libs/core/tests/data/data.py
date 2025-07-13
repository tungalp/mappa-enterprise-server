from uuid import UUID
from sqlalchemy import DDL, ForeignKey, Column, Integer, String, Uuid, event, text
from sqlalchemy.orm import relationship
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity import Base, EntityMixin, TenantMixin
from mapa.core.data.base_repository import BaseRepository
from typing import Type


class CustomerEntity(Base, EntityMixin, TenantMixin):
    __tablename__ = 'customers'

    name = Column(String)
    address = Column(String)
    email = Column(String)
    invoices = relationship("InvoiceEntity", back_populates="customer")


# @event.listens_for(CustomerEntity.__table__, 'after_create')
# def receive_after_create(target, connection, **kw):
#     connection.execute(
#          text(f"ALTER TABLE {CustomerEntity.__tablename__} ADD COLUMN test text")
#      )

    
class InvoiceEntity(Base, EntityMixin, TenantMixin):
    __tablename__ = 'invoices'

    invoice_no = Column(Integer)
    amount = Column(Integer)
    customer_id = Column(Uuid(), ForeignKey('customers.id'))
    customer = relationship("CustomerEntity", back_populates="invoices")

    company_id = Column(Uuid(), ForeignKey('companies.id'))
    company = relationship("CompanyEntity", back_populates="invoices")


class CompanyEntity(Base, EntityMixin, TenantMixin):
    __tablename__ = 'companies'

    name = Column(String)
    title = Column(String)
    invoices = relationship("InvoiceEntity", back_populates="company")
    owner_id = Column(Uuid(), ForeignKey('owners.id'))
    owner = relationship("OwnerEntity", back_populates="company")


class OwnerEntity(Base, EntityMixin, TenantMixin):
    __tablename__ = "owners"

    name = Column(String)
    surname = Column(String)
    company = relationship(
        "CompanyEntity", back_populates="owner", uselist=False)

o1 = OwnerEntity(name="test", surname="test", tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))
o2 = OwnerEntity(name="test2", surname="test2", tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))
cm1 = CompanyEntity(name="Microsoft", title="Microsoft", owner=o1, tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))
cm2 = CompanyEntity(name="Oracle", title="Oracle", owner=o2, tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))
c1 = CustomerEntity(id=UUID("500609a0-5a3f-45ab-aed9-b443ff3161b2"), name="Gopal Krishna",
                    address="Bank Street Hydarebad", email="gk@gmail.com", tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))
c2 = CustomerEntity(id=UUID("642da618-c1ca-4d59-9b29-314a5afafab1"), name="Zopal Krishna",
                    address="Bank Street Hydarebad", email="zk@gmail.com", tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))
c3 = CustomerEntity(id=UUID("d155385e-c222-4078-83f9-e6bf22907c9d"), name="Kopal Krishna",
                    address="Bank Street Hydarebad", email="kk@gmail.com", tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))

c1.invoices = [
    InvoiceEntity(invoice_no=1, amount=15000, company=cm1, tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")),
    InvoiceEntity(invoice_no=2, amount=3850, tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))
]
c2.invoices = [
    InvoiceEntity(invoice_no=3, amount=12000, tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")),
    InvoiceEntity(invoice_no=4, amount=7000, company=cm2, tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))
]
c3.invoices = [
    InvoiceEntity(invoice_no=5, amount=15000, company=cm1, tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")),
    InvoiceEntity(invoice_no=6, amount=5800, tenant_id=UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d"))
]
# Veritabanına test için kaydolacak kayıtlar
instances = [o1, o2, cm1, cm2, c1, c2, c3]

# Repository


class CustomerRepository(BaseRepository[CustomerEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, CustomerEntity)


class InvoiceRepository(BaseRepository[InvoiceEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, InvoiceEntity)


class CompanyRepository(BaseRepository[CompanyEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, CompanyEntity)


class OwnerRepository(BaseRepository[OwnerEntity]):
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OwnerEntity)

