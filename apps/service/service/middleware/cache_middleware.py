from fastapi import Request
from fastapi import Request
import hashlib
import json
from starlette.responses import Response
import base64


async def get_cache_key(request: Request):
    """Request'in body ve query parametrelerine göre cache key oluşturur."""
    body = await request.body()

    # Request body’yi tekrar kullanılabilir hale getirmek için yeniden oluştur
    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive

    query_params = dict(request.query_params)

    data = {
        "method": request.method,
        "path": request.url.path,
        "query": query_params,
        "body": body.decode("utf-8"),
    }

    key = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    return key


async def cache_middleware(request: Request, call_next):
    try:
        redis_read = request.app.state.redis_read
        key = await get_cache_key(request)

        cached_response = await redis_read.get(key)
        if cached_response:
            cache_data = json.loads(cached_response)
            if cache_data.get("is_base64"):
                body_bytes = base64.b64decode(cache_data["body"])
            else:
                body_bytes = cache_data["body"].encode()

            return Response(
                content=body_bytes,
                status_code=cache_data.get("status_code", 200),
                headers=cache_data.get("headers", {}),
                media_type=cache_data.get("media_type", "application/json")
            )

        response = await call_next(request)

        cache_second = response.headers.get("X-Cache-Second")
        cache_second = int(cache_second) if cache_second and cache_second != "None" else 0

        # body'i oku
        response_body = [section async for section in response.body_iterator]
        body_bytes = b"".join(response_body)

        if cache_second and cache_second > 0:
            redis_write = request.app.state.redis_write
            filtered_headers = {
                k: v for k, v in dict(response.headers).items()
                if k.lower() not in ["content-length", "transfer-encoding", "connection"]
            }
            cache_data = {
                "body": base64.b64encode(body_bytes).decode(),
                "status_code": response.status_code,
                "headers": filtered_headers,
                "media_type": response.media_type,
                "is_base64": True
            }
            await redis_write.set(key, json.dumps(cache_data, ensure_ascii=False, default=str), ex=cache_second)

        return Response(
            content=body_bytes,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

    except Exception:
        return await call_next(request)