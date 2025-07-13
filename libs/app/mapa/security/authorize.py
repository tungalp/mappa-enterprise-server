import inspect
from functools import wraps
from typing import Any, Callable, List
from starlette._utils import is_async_callable
from fastapi import HTTPException, Request, Response, WebSocket, status
from fastapi.requests import HTTPConnection


def has_required_scope(conn: HTTPConnection, scopes: List[str]) -> bool:
    """Verilen yetki listesinin tanımlı yetkileri kapsayıp kapsamadığına bakılır."""
    for scope in scopes:
        if scope not in conn.auth.scopes:
            return False
    return True

def authorize(scopes_list: List[str] | None = None) -> Callable:
    """Gelen isteğin yetkili bir kullanıcıdan gelip gelmediği kontrol edilir.
    """
    def decorator(func):
        sig = inspect.signature(func)
        for idx, parameter in enumerate(sig.parameters.values()):
            if parameter.name == "request" or parameter.name == "websocket":
                type_ = parameter.name
                break
        else:
            raise Exception(
                f'No "request" or "websocket" argument on function "{func}"'
            )

        if type_ == "websocket":
            # Handle websocket functions. (Always async)
            @wraps(func)
            async def websocket_wrapper(
                *args: Any, **kwargs: Any
            ) -> None:
                websocket = kwargs.get(
                    "websocket", args[idx] if idx < len(args) else None
                )
                assert isinstance(websocket, WebSocket)
                
                # if not has_required_scope(websocket, scopes_list):
                #     await websocket.close()
                # else:
                #     await func(*args, **kwargs)
                return await func(*args, **kwargs)
            return websocket_wrapper

        elif is_async_callable(func):
            # Handle async request/response functions.
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Response:
                request = kwargs.get("request", args[idx] if idx < len(args) else None)
                assert isinstance(request, Request)

                # Eğer kullanıcı login olmamışsa kimlk hatası döndürülür.
                if not request.user.is_authenticated:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not authenticated"
                    )

                if not has_required_scope(request, scopes_list or []):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Scope not supported"
                    )
                return await func(*args, **kwargs)
            return async_wrapper
    return decorator