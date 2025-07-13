import json
from uuid import uuid4
import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.constants import ApplicationTypes
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.organization_client.organization_client_model import CreateOrganizationClient
from mapa.manage.client.client_model import CreateClient
from .data import generate_organization_type,generate_organization,generate_organization_client
from .conftest import generate_client
from nanoid import generate

@pytest.mark.asyncio
async def test_paging(fixture):
    """Find metodunu test eder """

    async with fixture.client() as client:
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=str(uuid4())),
        ],
            order={
            "id": "desc"
        })
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        paging_response = await client.get(f"/api/manage/organization_client/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir organization_client id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        id = str(uuid4())
        response = await client.get(f"/api/manage/organization_client/{id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir organization_client id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        
        create_organization_type = generate_organization_type()
        create_organization_types = [create_organization_type]
        organization_type_content = json.dumps([obj.model_dump(exclude_none=True)
                                  for obj in create_organization_types], cls=JsonEncoder)
        create_organization_type_response = await client.post(f"/api/manage/organization_type/", content=organization_type_content)
        assert create_organization_type_response.status_code == 201
        organization_type_id = create_organization_type_response.json()['items'][0]['id']
        
        
        create_organization = generate_organization(organization_type_id)
        create_organizations = [create_organization]
        organization_content = json.dumps([obj.model_dump(exclude_none=True)
                                  for obj in create_organizations], cls=JsonEncoder)
        create_organization_response = await client.post(f"/api/manage/organization/", content=organization_content)
        assert create_organization_response.status_code == 201
        organization_id = create_organization_response.json()['items'][0]['id']
        
        create_client = CreateClient(
            name="client_test_organization"+generate(size=4),
            grant_types=["authorization_code"],
            application_type=ApplicationTypes.WEB,
            logo_url="https://www.islem.com.tr/application/views/islemgis/layouts/images/logo-colored.png") 
        
        create_clients = [create_client]
        client_content = json.dumps([obj.model_dump(exclude_none=True)
                                  for obj in create_clients], cls=JsonEncoder)
        create_client_response = await client.post(f"/api/manage/client/", content=client_content)
        assert create_client_response.status_code == 201
        client_id = create_client_response.json()['items'][0]['client_id']
        
        create_organization_client: CreateOrganizationClient = generate_organization_client(client_id,organization_id)
        create_organization_client_response = await client.post(
            "/api/manage/organization_client/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_organization_client]], cls=JsonEncoder)
        )
        assert create_organization_client_response.status_code == 201
        base_layer_id = create_organization_client_response.json()["items"][0]["id"]
        field_list = ["id", "client_id", "organization_id", "is_hierarchical"]
        response = await client.get(f'/api/manage/organization_client/{base_layer_id}?field_list={json.dumps(field_list)}')
    assert response.status_code == 200
    