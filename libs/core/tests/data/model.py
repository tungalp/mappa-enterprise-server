from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from mapa.core.data.async_db import AsyncDatabase

from mapa.core.data.base_entity_service import BaseEntityService
from tests.data.data import CustomerRepository, CustomerEntity


class CustomerModel(BaseModel):

    id: UUID
    name: str
    email: str
    address: Optional[str] = None
    invoices: Optional[List["InvoiceModel"]] = []


class CreateCustomer(BaseModel):
    name: str
    email: str
    address: Optional[str]


class UpdateCustomer(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class UpdateAllCustomer(BaseModel):
    address: Optional[str]


class InvoiceModel(BaseModel):

    id: UUID
    invoice_no: int
    amount: int
    customer_id: UUID
    customer: Optional[CustomerModel] = None

    company_id: Optional[UUID] = None
    company: Optional["CompanyModel"] = None


class CreateInvoice(BaseModel):
    invoice_no: int
    amount: int
    customer_id: UUID
    company_id: UUID


class UpdateInvoice(BaseModel):
    invoice_no: Optional[int]
    amount: Optional[int]
    customer_id: Optional[UUID]
    company_id: Optional[UUID]


class UpdateAllInvoice(BaseModel):
    amount: Optional[int]
    customer_id: Optional[UUID]
    company_id: Optional[UUID]


class OwnerModel(BaseModel):
    id: UUID
    name: str
    surname: str
    company_id: Optional[UUID]  = None
    company: Optional["CompanyModel"] = None


class CreateOwner(BaseModel):
    name: str
    surname: str


class UpdateOwner(BaseModel):
    name: Optional[str]
    surname: Optional[str]


class UpdateAllOwner(BaseModel):
    name: Optional[str]
    surname: Optional[str]


class CompanyModel(BaseModel):

    id: UUID
    name: str
    title: str
    invoices: Optional[List[InvoiceModel]] = []
    owner_id: UUID
    owner: Optional[OwnerModel]  = None


class CreateCompany(BaseModel):
    name: str
    title: str
    owner_id: UUID


class UpdateCompany(BaseModel):
    title: str


class UpdateAllCompany(BaseModel):
    title: str


OwnerModel.model_rebuild()
InvoiceModel.model_rebuild()
CompanyModel.model_rebuild()
CustomerModel.model_rebuild()

# Service


class CustomerService(BaseEntityService[CustomerRepository, CustomerModel, CreateCustomer, UpdateCustomer, UpdateAllCustomer]):

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, CustomerRepository, CustomerModel)
