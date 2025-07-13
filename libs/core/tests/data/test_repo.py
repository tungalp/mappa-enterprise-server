import asyncio

import pytest
from sqlalchemy import text
from mapa.core import __version__
from mapa.core.data.base_repository import BaseRepository
from mapa.core.data.query_args import Filter, FilterGroup, FilterOp, FilterType, QueryArgs
from ..conftest import CoreFixture
from tests.data.data import CustomerRepository


async def create_test_repo(fixture) -> CustomerRepository:
    """Test verisini oluşturduktan sonra  repository nesnesini oluşturur"""

    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    return CustomerRepository(async_db)


@pytest.mark.asyncio
async def test_set_tenant_id(fixture: CoreFixture):
    """Uygulama parametresinin veritabanı oturumuna set edilmesini test eder"""
    async_db = fixture.create_db_instance(fixture.db_url_async)
    async with async_db.session() as session:
        # set tenant_id
        tenant_id = 'tenant_1'
        await session.execute(text(f"set app.tenant_id='{tenant_id}'"))

        data = await session.execute(text("select current_setting('app.tenant_id')"))
        ret_val = data.scalars().first()
        assert tenant_id == ret_val


@pytest.mark.asyncio
async def test_get_without_fields(fixture: CoreFixture):
    """Repository"""
    repo: CustomerRepository = await create_test_repo(fixture)

    obj_id = "500609a0-5a3f-45ab-aed9-b443ff3161b2"
    customer = await repo.get(obj_id, fixture.tenant_id)
    assert customer is not None

    obj_dict = repo.model_dump(customer)
    assert "invoices" not in obj_dict

@pytest.mark.asyncio
async def test_get_all(fixture: CoreFixture):
    """Repository"""
    repo: CustomerRepository = await create_test_repo(fixture)

    field_list = [
        "id",
        "invoices.id",
        "invoices.customer.id",
        "invoices.customer.name",
        "invoices.company.id",
        "invoices.company.owner.id",
        "invoices.company.owner.name"
    ]
    query_args = QueryArgs(select=field_list)
    customer_list = await repo.find(query_args, fixture.tenant_id)
    assert len(customer_list) > 0

    
@pytest.mark.asyncio
async def test_get_with_fields(fixture: CoreFixture):
    """Repository"""
    repo: CustomerRepository = await create_test_repo(fixture)

    field_list = [
        "id",
        "invoices.id",
        "invoices.customer.id",
        "invoices.customer.name",
        "invoices.company.id",
        "invoices.company.owner.id",
        "invoices.company.owner.name"
    ]
    customer = await repo.get("500609a0-5a3f-45ab-aed9-b443ff3161b2", fixture.tenant_id, field_list)
    assert customer is not None

    #query_args = QueryArgs(where=[
    #    Filter(field="id", op=FilterOp.EQUAL,
    #           value="500609a0-5a3f-45ab-aed9-b443ff3161b2")], select=field_list)
    # data_list = await repo.find(query_args, fixture.tenant_id) 

    obj_dict = repo.model_dump(customer, field_list)
    assert obj_dict is not None


@pytest.mark.asyncio
async def test_find_with_limit_offset(fixture: CoreFixture):
    """QueryArgs parametrelerinden alan listesi oluşturmayı test eder"""

    repo = await create_test_repo(fixture)

    query_args = QueryArgs(limit=4, offset=2)
    data_list = await repo.find(query_args, fixture.tenant_id)

    assert len(data_list) > 0


@pytest.mark.asyncio
async def test_count(fixture: CoreFixture):
    """QueryArgs parametrelerinden alan listesi oluşturmayı test eder"""

    repo = await create_test_repo(fixture)

    query_args = QueryArgs(limit=4, offset=2)
    count = await repo.count(query_args, fixture.tenant_id)

    assert count > 0


@pytest.mark.asyncio
async def test_find_with_query_args(fixture: CoreFixture):
    """QueryArgs parametrelerinden alan listesi oluşturmayı test eder"""

    repo = await create_test_repo(fixture)

    query_args = QueryArgs(
        where=[
            Filter(field="id", op=FilterOp.EQUAL,
                   value="500609a0-5a3f-45ab-aed9-b443ff3161b2"),
            Filter(field="name", op=FilterOp.LIKE, value="Test"),
            Filter(field="name", op=FilterOp.ILIKE, value="Test2"),
            Filter(field="name", op=FilterOp.NOT_LIKE, value="Test"),
            Filter(field="name", op=FilterOp.NOT_ILIKE, value="Test2"),
            Filter(field="name", op=FilterOp.NULL),
            Filter(field="name", op=FilterOp.NOT_NULL),
            Filter(field="id", op=FilterOp.IN, value=[
                "500609a0-5a3f-45ab-aed9-b443ff3161b2", "d155385e-c222-4078-83f9-e6bf22907c9d"]),
            Filter(field="name", op=FilterOp.NOT_IN, value=["test", "test2"]),
            Filter(field="invoices.id", op=FilterOp.EQUAL,
                   value="b767f2ae-2840-47be-958f-21ff28337323"),
            Filter(field="invoices.company.id", op=FilterOp.MORE_THAN,
                   value="b767f2ae-2840-47be-958f-21ff28337323"),
            Filter(field="invoices.company.name",
                   op=FilterOp.EQUAL, value="name2"),
            Filter(field="invoices.company.owner.name",
                   op=FilterOp.EQUAL, value="name2"),
            FilterGroup(type=FilterType.AND, filters=[
                Filter(field="invoices.customer.name",
                       op=FilterOp.LIKE, value="name1"),
                Filter(field="invoices.company.owner.name",
                       op=FilterOp.EQUAL, value="name2")
            ]),
            FilterGroup(type=FilterType.OR, filters=[
                Filter(field="invoices.customer.name",
                       op=FilterOp.LIKE, value="name1"),
                Filter(field="invoices.company.owner.name",
                       op=FilterOp.EQUAL, value="name2")
            ])
        ],
        order={
            "invoices.customer.name": "asc",
            "name": "desc"
        },
        select=[
            "id",
            "invoices.id",
            "invoices.customer.id",
            "invoices.customer.name"
        ]
    )

    data_list = await repo.find(query_args, fixture.tenant_id)
    assert len(data_list) == 0


@pytest.mark.asyncio
async def test_crud(fixture: CoreFixture):
    """Crud işlemlerinin testi"""

    repo = await create_test_repo(fixture)

    # Yeni test kayıtları oluşturulur
    el_count = 10  # min 3 olmalıdır.
    task_list = (
        repo.create({
            "name": f"Customer {i}",
            "email": f"customer_{i}@gmail.com"
        }, fixture.tenant_id) for i in range(1, el_count + 1)
    )

    customers = await asyncio.gather(*task_list)
    assert customers is not None
    assert len(customers) == el_count

    # Id listesine göre kayıtları getir
    selected_customers = await repo.find(QueryArgs(where=[
        Filter(field="id", op=FilterOp.IN, value=[c.id for c in customers])
    ], order={
        "name": "desc"
    }), fixture.tenant_id)
    assert len(selected_customers) == el_count

    # ilk elemanın email adresi değiştirilir
    test_email = "test@test.com"
    first_cust = customers[0]

    updated_first_cust = await repo.update(first_cust.id, {
        "email": test_email
    }, fixture.tenant_id)
    assert updated_first_cust is not None
    assert str(updated_first_cust.email) == test_email

    # İsmi Customer ile başlayan tüm elemanların ismi mobidik olarak değiştirilir
    query_args_update = QueryArgs(where=[
        Filter(field="name", op=FilterOp.LIKE, value="Customer%")
    ])
    test_name = "mobidik"
    updated_el_count = await repo.update_all(query_args_update, {
        "name": test_name
    }, fixture.tenant_id)
    assert updated_el_count > 0
    
    # ilk elemanı sorgulanır
    first_cust = await repo.get(first_cust.id, fixture.tenant_id)
    assert first_cust is not None
    assert str(first_cust.name) == test_name

    # Sorgu kriterine uyan ilk kayıt getirilir
    first_cust_2 = await repo.find_one(QueryArgs(where=[
        Filter(field="name", op=FilterOp.EQUAL, value=test_name),
    ]), fixture.tenant_id)
    assert first_cust_2 is not None
    
    # Update by ids
    ids = [str(first_cust.id), str(first_cust_2.id)]
    test_name = "mobidik 2"
    all_ids_updated = await repo.update_by_ids(ids, {
        "name": test_name
    }, fixture.tenant_id)
    assert all_ids_updated is True

    # ilk kayıt silinir
    first_row_deleted = await repo.delete(first_cust.id, fixture.tenant_id)
    assert first_row_deleted is True

    # Son iki kayıt silinir
    last_customer_ids = [cust.id for cust in customers[-2:]]
    deleted_row_count = await repo.delete_by_ids(last_customer_ids, fixture.tenant_id)
    # İsmi güncellenen iki kayıttan biri silindiğinden dolayı bir tane kalır
    assert deleted_row_count == 2

    # Kayıtlar silinir
    query_args_delete = QueryArgs(where=[
        Filter(field="name", op=FilterOp.EQUAL, value=test_name)
    ])
    deleted_row_count = await repo.delete_all(query_args_delete, fixture.tenant_id)
    assert deleted_row_count == 1

    # Silinenler sorgulanır
    deleted_rows = await repo.find(query_args_delete, fixture.tenant_id)
    assert len(deleted_rows) == 0
    
    


@pytest.mark.asyncio
async def test_expand_list(fixture: CoreFixture):
    """Verilen alan listesinden oluşan expand listesini kontrole eder."""
    repo = await create_test_repo(fixture)

    #  field list
    field_list = [
        "id",
        "invoices.id",
        "invoices.customer.id",
        "invoices.customer.name",
        "invoices.company.id",
        "invoices.company.owner.id",
        "invoices.company.owner.name"
    ]

    expand_list = repo._BaseRepository__create_expand_list(field_list) # type: ignore
    assert expand_list is not None
    assert expand_list == [
        "invoices",
        "invoices.customer",
        "invoices.company",
        "invoices.company.owner"
    ]


@pytest.mark.asyncio
async def test_create_field_list(fixture: CoreFixture):
    """Repository.dict test"""
    repo = await create_test_repo(fixture)

    obj_dict = repo._BaseRepository__create_select_tree([ # type: ignore
        "id",
        "invoices.id",
        "invoices.customer.id",
        "invoices.customer.name",
        "invoices.company.id",
        "invoices.company.owner.id",
        "invoices.company.owner.name"
    ])
    assert obj_dict is not None
    assert obj_dict == [
        "id",
        {
            "name": "invoices",
            "fields": [
                "id",
                {
                    "name": "customer",
                    "fields": [
                        "id",
                        "name"
                    ]
                },
                {
                    "name": "company",
                    "fields": [
                        "id",
                        {
                            "name": "owner",
                            "fields": [
                                "id",
                                "name"
                            ]
                        }
                    ]
                }
            ]
        },
    ]


@pytest.mark.asyncio
async def test_create_field_list_from_query_args(fixture: CoreFixture):
    """QueryArgs parametrelerinden alan listesi oluşturmayı test eder"""

    repo = await create_test_repo(fixture)

    query_args = QueryArgs(
        where=[
            Filter(field="id", op=FilterOp.MORE_THAN, value="123"),
            FilterGroup(type=FilterType.AND, filters=[
                Filter(field="invoices.customer.name",
                       op=FilterOp.LIKE, value="name1"),
                Filter(field="invoices.company.owner.name",
                       op=FilterOp.EQUAL, value="name2")
            ]),
            FilterGroup(type=FilterType.OR, filters=[
                Filter(field="invoices.customer.name",
                       op=FilterOp.LIKE, value="name1"),
                Filter(field="invoices.company.owner.name",
                       op=FilterOp.EQUAL, value="name2")
            ])
        ],
        order={
            "invoices.company.id": "desc",
            "invoices.company.name": "asc",
            "name": "desc"
        },
        select=[
            "id",
            "invoices.id",
            "invoices.customer.id",
            "invoices.customer.name"
        ]
    )
    field_list = repo._BaseRepository__create_field_list(query_args) # type: ignore 

    assert field_list == [
        "id",
        "invoices.id",
        "invoices.customer.id",
        "invoices.customer.name",
        "invoices.company.owner.name",
        "invoices.company.id",
        "invoices.company.name",
        "name"
    ]
