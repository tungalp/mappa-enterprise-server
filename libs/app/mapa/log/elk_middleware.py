import ast
import fnmatch
import json
import logging
import time
import asyncio
from typing import Any, Dict
from uuid import uuid4
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from logstash_async.handler import AsynchronousLogstashHandler


class ElkMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        application_name: str,
        host: str,
        port: int,
        env: str,
        redact_fields: list[str] = [],
        excluded_paths: list[str] = [],
    ):
        super().__init__(app)
        self.application_name = application_name
        self.host = host
        self.port = port
        self.env = env
        self.excluded_paths = excluded_paths
        self.redact_fields = redact_fields
        self.logger = logging.getLogger("esp_backend_logs")
        handler = AsynchronousLogstashHandler(self.host, self.port, database_path="logstash_backup.db")
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        self.log_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=10000)
        asyncio.create_task(self._worker_loop())

    async def _worker_loop(self):
        while True:
            await asyncio.sleep(0.5)
            items = []
            for _ in range(min(1000, self.log_queue.qsize())):
                try:
                    items.append(self.log_queue.get_nowait())
                except asyncio.QueueEmpty:
                    break

            for log_item in items:
                try:
                    level = log_item.pop("level", "INFO")
                    message = log_item.pop("message", "")

                    raw_req = log_item.pop("raw_request", {})
                    raw_res = log_item.pop("raw_response", {})

                    log_item["request"] = self.__redact_fields(raw_req)
                    log_item["response"] = self.__redact_fields(raw_res)

                    self.logger.log(getattr(logging, level), message, extra=log_item)
                except Exception as e:
                    print(f"Log sending failed: {e}")
                finally:
                    self.log_queue.task_done()

    async def dispatch(self, request: Request, call_next):
        start_log = time.time()
        path = request.url.path.lower()
        for excluded in self.excluded_paths:
            if excluded.endswith("*"):
                if path.startswith(excluded[:-1]):
                    return await call_next(request)
            elif path == excluded:
                return await call_next(request)

        audit_rid = str(uuid4())
        access_rid = str(uuid4())
        response = None
        req_body = b""
        res_body = b""
        process_time = ""
        try:
            start = time.time()
            req_body = await request.body()

            async def receive():
                return {"type": "http.request", "body": req_body}

            request._receive = receive

            response = await call_next(request)
            duration_ms = (time.time() - start) * 1000
            process_time = f"{duration_ms:.2f}ms"
            response.headers["X-Process-Rid"] = audit_rid
            status_code = response.status_code

            async for chunk in response.body_iterator:
                res_body += chunk
            response = Response(
                content=res_body,
                status_code=status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

            log_level = logging.INFO
            if status_code >= 500:
                log_level = logging.ERROR
            elif status_code >= 400:
                log_level = logging.WARNING

            log_common = dict(
                env=self.env,
                application={"name": self.application_name},
                completed_in=process_time,
                user=self.__get_user(request),
                client={"host": request.client.host, "port": request.client.port},
                path=request.url.path,
                status_code=response.status_code,
            )
            try:
                self.log_queue.put_nowait(
                    {
                        "level": logging.getLevelName(log_level),
                        "message": "access log",
                        "rid": access_rid,
                        "log_type": "access",
                        **log_common,
                        "raw_request": {},
                        "raw_response": {},
                    }
                )
            except asyncio.QueueFull:
                self.logger.warning("access log discarded due to full queue")

            try:
                self.log_queue.put_nowait(
                    {
                        "level": logging.getLevelName(log_level),
                        "message": "audit log",
                        "rid": audit_rid,
                        "log_type": "audit",
                        **log_common,
                        "raw_request": {
                            "url": str(request.url),
                            "path": request.url.path,
                            "headers": dict(request.headers),
                            "query_params": dict(request.query_params),
                            "path_params": request.path_params,
                            "body": req_body,
                        },
                        "raw_response": {
                            "status_code": response.status_code,
                            "body": res_body,
                        },
                    }
                )

                duration_ms_log = (time.time() - start) * 1000
                return response
            except asyncio.QueueFull:
                self.logger.warning("audit log discarded due to full queue")
                return response

        except Exception as ex:
            try:
                self.log_queue.put_nowait(
                    {
                        "level": "ERROR",
                        "message": "error log",
                        "rid": audit_rid,
                        "env": self.env,
                        "application": {"name": self.application_name},
                        "completed_in": process_time,
                        "raw_request": {
                            "url": str(request.url),
                            "path": request.url.path,
                            "headers": dict(request.headers),
                            "query_params": dict(request.query_params),
                            "path_params": request.path_params,
                            "body": req_body,
                        },
                        "raw_response": {"status_code": 500, "body": b""},
                        "user": self.__get_user(request),
                        "client": {
                            "host": request.client.host,
                            "port": request.client.port,
                        },
                        "exception": {
                            "type": ex.__class__.__name__,
                            "message": str(ex),
                        },
                        "log_type": "error",
                    }
                )
            except asyncio.QueueFull:
                self.logger.warning("error log discarded due to full queue")

            # If response is None (exception occurred before call_next), create an error response
            if response is None:
                response = Response(
                    content=json.dumps({"error": "Internal server error"}),
                    status_code=500,
                    headers={"Content-Type": "application/json"},
                    media_type="application/json",
                )
            return response

    def __get_user(self, request: Request):
        try:
            user = getattr(request, "user", None)
            if user:
                return {
                    "user_id": getattr(user, "sub", ""),
                    "tenant_id": getattr(user, "tenant_id", ""),
                    "is_authenticated": getattr(user, "is_authenticated", False),
                }
        except Exception:
            pass
        return None

    def __redact_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        def redact(value: Any) -> Any:
            if isinstance(value, dict):
                return {
                    k: redact(v) if not self.__is_redacted(k) else "[REDACTED]"
                    for k, v in value.items()
                }
            elif isinstance(value, list):
                return [redact(item) for item in value]
            elif isinstance(value, bytes):
                try:
                    return value.decode("utf-8", errors="ignore")
                except:
                    return "[UNDECODABLE]"
            elif isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, dict):
                        return json.dumps(self.__redact_fields(parsed))
                except:
                    pass
            return value

        return redact(data)

    def __is_redacted(self, key: str) -> bool:
        return any(
            fnmatch.fnmatch(key.lower(), pat.lower()) for pat in self.redact_fields
        )
