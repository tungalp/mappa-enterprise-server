from uuid import uuid4
from mapa.application.content_page.content_page_model import CreateContentPage
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from ..data import generate_app, generate_content_page
import pytest
import json


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
        paging_response = await client.get(f"/api/application/content_page/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir api id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        content_page_id = str(uuid4())
        response = await client.get(f"/api/application/content_page/{content_page_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_success(fixture):
    """Find metodunu test eder, varolan bir api id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_app = generate_app()
        create_apps = [create_app]
        create_apps_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in create_apps], cls=JsonEncoder)
        create_app_response = await client.post(f"/api/application/app/", content=create_apps_content)

        assert create_app_response.status_code == 201

        app_id = create_app_response.json()['items'][0]['id']

        create_content_page: CreateContentPage = generate_content_page(app_id)
        create_content_pages = [create_content_page]
        create_content_page_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in create_content_pages], cls=JsonEncoder)
        create_content_page_response = await client.post(f"/api/application/content_page/", content=create_content_page_content)

    assert create_content_page_response.status_code == 201
