from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs


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
        paging_response = await client.get(f"/api/spatial/layer_hook/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir layer id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        layer_hook_id = str(uuid4())
        response = await client.get(f"/api/spatial/layer_hook/{layer_hook_id}")

    assert response.status_code == 404


# @pytest.mark.asyncio
# async def test_find_create_success(fixture):
#     """Create metodunu test eder, varolan bir layer id olduğu için 200 dönmesi gerekiyor. """

#     async with fixture.client() as client:

#         create_gateway_api: CreateGatewayApi = generate_gateway_api()
#         create_gateway_api_response = await client.post(f"/api/gateway/gateway_api/", content=create_gateway_api.json(exclude_none=True))
#         assert create_gateway_api_response.status_code == 201

#         create_route: CreateRoute = generate_route(
#             create_gateway_api_response.json()["items"][0]["id"])
#         create_route_response = await client.post(f"/api/gateway/route/", content=create_route.json(exclude_none=True))
#         assert create_route_response.status_code == 201

#         create_connection: CreateConnection = generate_connection()
#         create_connection_response = await client.post(
#             "/api/spatial/connection/",
#             content=json.dumps([obj.model_dump(exclude_none=True)
#                                for obj in [create_connection]], cls=JsonEncoder)
#         )

#         create_layer: CreateLayer = generate_layer(
#             create_connection_response.json()["items"][0]["id"])
#         create_layer_response = await client.post(
#             "/api/spatial/layer/",
#             content=json.dumps([obj.model_dump(exclude_none=True)
#                                for obj in [create_layer]], cls=JsonEncoder)
#         )

#         layer_def_query_args: QueryArgs = QueryArgs(where=[
#             Filter(field="layer_id", op=FilterOp.EQUAL,
#                    value=create_layer_response.json()["items"][0]["id"]),
#         ],
#             order={
#             "id": "desc"
#         })
#         layer_def_query = layer_def_query_args.json()
#         layer_def_query_string = f"query={layer_def_query}"
#         layer_def_paging_response = await client.get(f"/api/spatial/layer_definition/?{layer_def_query_string}")

#         create_layer_hook: CreateLayerHook = generate_layer_hook(
#             create_route_response.json()["items"][0]["id"], layer_def_paging_response.json()["items"][0]["id"], HookOperationType.GET)

#         create_layer_hook_response = await client.post(
#             "/api/spatial/layer_hook/",
#             content=json.dumps([obj.model_dump(exclude_none=True)
#                                for obj in [create_layer_hook]], cls=JsonEncoder)
#         )

#         layer_hook_id = create_layer_hook_response.json()["items"][0]["id"]
#         field_list = ["id", "route_id", "layer_definition_id",
#                       "widget_name", "hook_operation_type"]
#         response = await client.get(f'/api/spatial/layer_hook/{layer_hook_id}?field_list={json.dumps(field_list)}')
#         assert response.status_code == 200

#     assert create_layer_hook_response.status_code == 201
