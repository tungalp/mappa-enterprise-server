import asyncio
import pytest
from mapa.core import __version__
from mapa.core.data.base_repository import BaseRepository
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.result import PagingResult
from ..conftest import CoreFixture
from .model import CreateCustomer, CustomerService, UpdateAllCustomer, UpdateCustomer, CustomerModel


async def create_test_service(fixture) -> CustomerService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    return CustomerService(async_db)


@pytest.mark.asyncio
async def test_create_service(fixture: CoreFixture):
    """Service"""
    service: CustomerService = await create_test_service(fixture)

    assert service is not None


@pytest.mark.asyncio
async def test_get_all(fixture: CoreFixture):
    """Service"""
    service: CustomerService = await create_test_service(fixture)
    assert service is not None

    field_list = [
        "id", "name", "email",
        "invoices.id", "invoices.invoice_no", "invoices.amount", "invoices.customer_id", "invoices.company_id",
        "invoices.company.id", "invoices.company.name", "invoices.company.title", "invoices.company.owner_id",
        "invoices.company.owner.id", "invoices.company.owner.name", "invoices.company.owner.surname"
    ]

    query_args = QueryArgs(select=field_list)
    customer_list = await service.find(query_args, fixture.tenant_id)
    assert len(customer_list) > 0


@pytest.mark.asyncio
async def test_get_with_model(fixture: CoreFixture):
    """Service"""
    service: CustomerService = await create_test_service(fixture)
    assert service is not None

    model = ["id", "name", "email", {
        "invoices": ["id", "invoice_no", "amount", "customer_id", "customer_id", {
            "company": ["id", "name", "title", "owner_id", {
                "owner": ["id", "name", "surname"]
            }]
        }]
    }]

    customer = await service.create(CreateCustomer(
        name=f"Customer", email=f"customer@gmail.com", address=""), fixture.tenant_id
    )
    assert customer is not None
    
    customer2 = await service.get(customer.id, fixture.tenant_id, model)
    assert customer2 is not None

    deleted = await service.delete(customer2.id, fixture.tenant_id)
    assert deleted


@pytest.mark.asyncio
async def test_get_all_with_model(fixture: CoreFixture):
    """Service"""
    service: CustomerService = await create_test_service(fixture)
    assert service is not None

    model = ["id", "name", "email", {
        "invoices": ["id", "invoice_no", "amount", "customer_id", "customer_id", {
            "company": ["id", "name", "title", "owner_id", {
                "owner": ["id", "name", "surname"]
            }]
        }]
    }]

    query_args = QueryArgs(model=model)
    customer_list = await service.find(query_args, fixture.tenant_id)
    assert len(customer_list) > 0


@pytest.mark.asyncio
async def test_crud(fixture: CoreFixture):
    """Service"""
    service: CustomerService = await create_test_service(fixture)
    assert service is not None

    # Yeni test kayıtları oluşturulur
    el_count = 10
    task_list = (service.create(CreateCustomer(
        name=f"Customer {i}", email=f"customer_{i}@gmail.com", address=""), fixture.tenant_id) for i in range(1, el_count + 1))
    customers = await asyncio.gather(*task_list)
    assert customers is not None
    assert len(customers) >= el_count

    # Sayfa parametrelerine göre kayıtları getirir.
    paging_result = await service.paging(QueryArgs(limit=4, offset=2), tenant_id=fixture.tenant_id)
    assert len(paging_result.items) == 4
    assert paging_result.limit == 4
    assert paging_result.offset == 2

    # Id listesine göre kayıtları getir
    selected_customers = await service.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[
               str(c.id) for c in customers])
    ], order={
        "name": "desc"
    }), fixture.tenant_id)
    assert len(selected_customers) == el_count

    # ilk elemanın email adresi değiştirilir
    test_email = "test@test.com"
    first_cust = customers[0]

    updated_first_cust = await service.update(first_cust.id, UpdateCustomer(
        email=test_email
    ), fixture.tenant_id)
    assert updated_first_cust is not None
    assert updated_first_cust.email == test_email

    # İsmi Customer ile başlayan tüm elemanların ismi mobidik olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="name", op=FilterOp.LIKE, value="Customer%")
    ])

    test_address = "test_address"
    updated_el_count = await service.update_all(query_args_update, UpdateAllCustomer(
        address=test_address
    ), fixture.tenant_id)
    assert updated_el_count == len(customers)

    # ilk elemanı sorgulanır
    first_cust = await service.get(first_cust.id)
    assert first_cust is not None
    assert first_cust.address == test_address

    # ilk kayıt silinir
    first_row_deleted = await service.delete(first_cust.id, fixture.tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_customer_ids = [cust.id for cust in customers[-2:]]
    deleted_row_count = await service.delete_by_ids(last_customer_ids, fixture.tenant_id)
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="address", op=FilterOp.EQUAL, value=test_address)
    ])
    deleted_row_count = await service.delete_all(query_args_delete, fixture.tenant_id)
    # 3 kayıt önceden silindiğinden dolayı
    assert deleted_row_count == len(customers) - 3

    # Silinenler sorgulanır
    deleted_rows = await service.find(query_args_delete, fixture.tenant_id)
    assert len(deleted_rows) == 0


@pytest.mark.asyncio
async def test_select_with_child(fixture: CoreFixture):
    """Service"""
    service: CustomerService = await create_test_service(fixture)
    assert service is not None

    # Sayfa parametrelerine göre kayıtları getirir.
    paging_result: PagingResult[CustomerModel] = await service.paging(QueryArgs(
        select=[
            "id",
            "name",
            "email",
            "invoices.id",
            "invoices.invoice_no",
            "invoices.amount",
            "invoices.customer_id",
            "invoices.company_id",
        ],
        limit=10,
        offset=0,
        where=[
            Filter(field="invoices.invoice_no",
                   op=FilterOp.MORE_THAN, value=3)  # 4, 5, 6
        ]
    ), tenant_id=fixture.tenant_id)

    assert len(paging_result.items) == 2
    assert paging_result.items[0].invoices is not None
    assert paging_result.items[0].invoices[0].invoice_no in [4, 5, 6]
    assert paging_result.limit == 10
    assert paging_result.offset == 0
