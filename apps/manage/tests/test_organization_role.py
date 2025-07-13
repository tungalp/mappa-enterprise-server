import json
from uuid import uuid4
import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType
from mapa.manage.organization.organization_model import CreateOrganization
from mapa.manage.organization_role.organization_role_model import CreateOrganizationRole
from mapa.manage.role.role_model import CreateRole
from .data import generate_organization_type,generate_organization,generate_organization_role
from .conftest import generate_role

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
        paging_response = await client.get(f"/api/manage/organization_role/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir organization_role id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        id = str(uuid4())
        response = await client.get(f"/api/manage/organization_role/{id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir organization_role id olduğu için 200 dönmesi gerekiyor. """

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
        
        create_role = generate_role()
        create_roles = [create_role]
        role_content = json.dumps([obj.model_dump(exclude_none=True)
                                  for obj in create_roles], cls=JsonEncoder)
        create_role_response = await client.post(f"/api/manage/role/", content=role_content)
        assert create_role_response.status_code == 201
        role_id = create_role_response.json()['items'][0]['id']
        
        create_organization_role: CreateOrganizationRole = generate_organization_role(role_id,organization_id)
        create_organization_role_response = await client.post(
            "/api/manage/organization_role/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_organization_role]], cls=JsonEncoder)
        )
        assert create_organization_role_response.status_code == 201
        base_layer_id = create_organization_role_response.json()["items"][0]["id"]
        field_list = ["id", "role_id", "organization_id"]
        response = await client.get(f'/api/manage/organization_role/{base_layer_id}?field_list={json.dumps(field_list)}')
    assert response.status_code == 200
    