from datetime import datetime, timedelta
import pathlib
import uuid

from bcrypt import gensalt, hashpw
import nanoid
from mapa.sso.authorization_code.authorization_code_entity import AuthorizationCodeEntity
from mapa.manage.api.api_entity import ApiEntity
from mapa.manage.client.client_entity import ClientEntity
from mapa.manage.client_api.client_api_entity import ClientApiEntity
from mapa.manage.client_api_scope.client_api_scope_entity import ClientApiScopeEntity
from mapa.manage.tenant.tenant_entity import TenantEntity
from mapa.manage.tenant_client.tenant_client_entity import TenantClientEntity
from mapa.manage.user.user_entity import UserEntity
from mapa.manage.role.role_entity import RoleEntity
from mapa.manage.constants import LevelTypes
from mapa.sso.jwk.jwk_entity import JwkEntity
from mapa.sso.user_session.user_session_entity import UserSessionEntity
from mapa.manage.tenant_user.tenant_user_entity import TenantUserEntity
from mapa.sso.user_session_client.user_session_client_entity import UserSessionClientEntity


user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")
user = UserEntity(
    id=user_id,
    name="admin",
    surname="admin",
    email="admin@admin.com",
    password=hashpw("admin".encode("utf-8"), gensalt()).decode("utf-8")
)

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
tenant = TenantEntity(
    id=tenant_id,
    name="Admin",
    title="Admin Tenant",
    user_id=user_id
)
tenant_user = TenantUserEntity(
    user_id=user_id,
    tenant_id=tenant_id,
    role="owner"
)

user_2_id = uuid.UUID("2d943171-9c9e-4c95-806a-566bd725a436")
user2 = UserEntity(
    id=user_2_id,
    name="member",
    surname="member",
    email="member@member.com",
    password=hashpw("member".encode("utf-8"), gensalt()).decode("utf-8")
)

tenant_2_id = uuid.UUID("85e94027-6edd-4053-b518-8a195f10edbf")
tenant2 = TenantEntity(
    id=tenant_2_id,
    name="Member",
    title="Member Tenant",
    user_id=user_2_id
)
tenant_2_user = TenantUserEntity(
    user_id=user_2_id,
    tenant_id=tenant_2_id,
    role="owner"
)

session_id = uuid.UUID("e7966430-19c8-4e70-acdd-8737ff67cce9")
user_session = UserSessionEntity(
    id=session_id,
    user_id=user_id,
    authenticated_at=datetime.now(),
    expired_at=datetime.now() + timedelta(days=365),
    authenticated=True
)

client_id_manage = uuid.UUID("fa2518dd-5b27-4a59-b740-e96c3c79160a")
client_manage = ClientEntity(
    id=client_id_manage,
    name="manage",
    client_id="client_id_manage",
    client_secret="client_secret_manage",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:33001/callback",
                   "http://localhost:33001/callback_silent"],    
    is_system=True,
    level_type= LevelTypes.FIRST_PARTY,
    require_pkce=True
)
tenant_client_manage = TenantClientEntity(
    client_id=client_id_manage,
    tenant_id=tenant_id
)

client_id_workspace = uuid.UUID("891981ea-85ba-40bb-b150-409e339e5b65")
client_workspace = ClientEntity(
    id=client_id_workspace,
    name="workspace",
    client_id="client_id_workspace",
    client_secret="client_secret_workspace",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:33002/callback",
                   "http://localhost:33002/callback_silent"],    
    is_system=True,
    level_type= LevelTypes.FIRST_PARTY,
    require_pkce=True
)
tenant_client_workspace = TenantClientEntity(
    client_id=client_id_workspace,
    tenant_id=tenant_id
)

user_session_client_id = uuid.UUID("fb0ce2e7-49de-4ad9-aab0-8e2d7d1fddcc")
user_session_client = UserSessionClientEntity(
    id=user_session_client_id,
    user_session_id=session_id,
    client_id=client_id_manage,
    tenant=tenant_id,
    created_at=datetime.now()
)

client_id_gateway = uuid.UUID("858b742b-29d1-469d-87d7-9095ef0fcbf0")
client_gateway = ClientEntity(
    id=client_id_gateway,
    name="gateway",
    client_id="client_id_gateway",
    client_secret="client_secret_gateway",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:3003/callback"],
    is_system=True,
    level_type= LevelTypes.FIRST_PARTY,
    require_pkce=True
)
tenant_client_gateway = TenantClientEntity(
    client_id=client_id_gateway,
    tenant_id=tenant_id
)

client_id_test = uuid.UUID("d858b93d-5b5b-49b6-8302-9f96be0ea36a")
client_test = ClientEntity(
    id=client_id_test,
    name="test",
    client_id="client_id_test",
    client_secret="client_secret_test",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:3000"],
    is_system=True,
    level_type= LevelTypes.THIRD_PARTY,
    require_pkce=False
)
tenant_client_test = TenantClientEntity(
    client_id=client_id_test,
    tenant_id=tenant_id
)

client_id_test_2 = uuid.UUID("7c17eed3-e345-4d83-875c-d1a053a436b9")
client_test_2 = ClientEntity(
    id=client_id_test_2,
    name="test2",
    client_id="client_id_test_2",
    client_secret="client_secret_test_2",
    grant_types=["authorization_code", "refresh_token", "hybrid"],
    redirect_uris=["http://localhost:3000"],
    level_type= LevelTypes.THIRD_PARTY,
    require_pkce=False
)
tenant_client_test_2 = TenantClientEntity(
    client_id=client_id_test_2,
    tenant_id=tenant_2_id
)

nonce = "B6XMlQUsILYjf7oK9ElT1"
audience = "https://test-server/api/v1"
auth_code = AuthorizationCodeEntity(
    client_id="client_id_manage",
    user_session_id=session_id,
    user_id=user_id,
    audience=audience,
    scopes=["openid", "profile", "email", "offline_access"],
    redirect_uri="http://localhost:33001/manage/callback",
    code_challenge="XBzLH5tHF7Z-_U2Rqr8BT0uYJ3SeTqd5mfNwSL0Ig-o",
    code_challenge_method="S256",
    code="1234567890abc",
    nonce=nonce,
    created_at=datetime.now(),
    expired_at=datetime.now() + timedelta(minutes=10)
)

# 15 gün önce 
old_jwk_id = uuid.UUID("7e439fd3-0c16-4c80-93c7-3b924fa78c3c")
old_jwk = JwkEntity(
    id=old_jwk_id,
    key_id = nanoid.generate(),
    private_pem="private_pem_old",
    public_pem="public_pem_old",
    jwk={
        "kid": nanoid.generate()
    },
    created_at=datetime.now() - timedelta(days=45),
    expired_at=datetime.now() - timedelta(days=15),
)

# 15 gün sonra 
new_jwk_id = uuid.UUID("09ee9593-1acb-4611-b77e-8a7bc0d631a8")
new_jwk = JwkEntity(
    id=new_jwk_id,
    key_id = nanoid.generate(),
    private_pem="private_pem_new",
    public_pem="public_pem_new",
    jwk={
        "kid": nanoid.generate()
    },
    created_at=datetime.now() - timedelta(days=15),
    expired_at=datetime.now() + timedelta(days=15),
)

instances = [
    user, tenant, tenant_user, user2, tenant2, tenant_2_user,
    client_manage, tenant_client_manage,
    client_workspace, tenant_client_workspace,
    client_gateway, tenant_client_gateway,
    client_test, tenant_client_test,
    client_test_2, tenant_client_test_2,
    user_session, auth_code, user_session_client,
    old_jwk, new_jwk
]


def read_file(file_name: str) -> str:
    content = ""
    path = pathlib.Path(file_name)
    if not path.is_absolute():
        full_path = path.joinpath(path.home(), file_name)
    else:
        full_path = file_name
    with open(full_path, "r") as f:
        content = f.read()
    return content


# Test keys for development/testing only
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAv5GICUgxFvFHKM4PMnkxuQz4mH4eYuXG4nKdYi7Tqw9A7Ixr
TJqAljc5fL4h1QEbZqGRwvXkFGzY1cXY0+Y8/L2jzaJK1L9R5RVLp7r2PD1M5XrD
XoXHHpJ5KiXuKFPqD1vvXCEaUhwh3gXy94fPXutxqDZhKXBqXPDovz8ZTzAPs2ru
f1j7Kz4gZj3YJyV4HvT9n4bAn9tZ0wKxX5ZkOvwJHU+FoY0ARDYa1HdIH4WP92Bj
YYD1yGJXBP+okQtQGPyJbFZwbBLcHqY0pIGJHPly9UQZHxh1jFm0MsEFhXxuqhD6
UNS0AJUzGZqQG6sKxH3I7M4Vc3DyKZXPjwpXNQIDAQABAoIBADLJ8r8MxZtHPWvD
Jz8Zjc1kzj9jMp4JKXqhwFZGe+HYWkyNUw5PtGJBK0Em5DEgpE4V8z3XeHJ/yfcE
wOKVQlP5oQJ8vJ5T5oYCJX2RD1Q5zGz6IuB3Kk9Ph2TtU5n0DJqHRZYPUEwHcVqR
mB5TqJ4ZcLUGvj5p5+LhYX5RvY5RJ5xFSOc94JYzNp4qI2Nf0CQJ5/1zL8RxgUYB
KTqGPmZ8YYQY5yLGJHoX5Eo5Tl4/BnL5X5YFvY4XqhzCEAjV3vfZVxJJw6t7KZJX
Q7uxxQ6/WNtM2+JZwFX8aI8HZl3wDzrHHYZZEEKUQGxGZLkB2WXJ0Yj5qYMZvxUC
gYEA3Q8JCf8KJHZZUQkzGqYJQ5NZ4ERx6vxnqGHG6G6RaxHCDQs+4hgXdHHx5yGE
8JKxH4WqZZqBWQ7xQzqL3ntQv5D0P5VeyJ1oFX5L3x7Q8lhgYx7mZ9Z3QH8YQXJL
MCgcAoIBAQDdDwkJ/woUdllRCTMapglDk1ngRHHq/GeoYcbobpFrEcINCz7iGBd0
cfHnIYTwkrEfhaplmoFZDvFDOove1C/kPQ/lV7InWgVfkvfHtDyWGBjHuZn1ndAf
xhBcUswKBwCggEBAOUZVBzqzqMKKuSWuPPGJKZJWUr7kI+qEW3CrgzCHjWJYTUQk
pjx9j8k3EaZZ4qGrJJIjJ5D0QFhxXJKjGd+4P6U4QOYJIHh/dKBxh5xKQtGEwYGI
eV4CMqII3F8qx8DJQrNfx8DGJ5eRg9YcYYI6jYHvOw5rAJsR8IvBqS+HKbUvZhkC
gYEA3Q8JCf8KJHZZUQkzGqYJQ5NZ4ERx6vxnqGHG6G6RaxHCDQs+4hgXdHHx5yGE
8JKxH4WqZZqBWQ7xQzqL3ntQv5D0P5VeyJ1oFX5L3x7Q8lhgYx7mZ9Z3QH8YQXJL
MCgcAoIBAQDdDwkJ/woUdllRCTMapglDk1ngRHHq/GeoYcbobpFrEcINCz7iGBd0
cfHnIYTwkrEfhaplmoFZDvFDOove1C/kPQ/lV7InWgVfkvfHtDyWGBjHuZn1ndAf
xhBcUswKBwCggEBAOUZVBzqzqMKKuSWuPPGJKZJWUr7kI+qEW3CrgzCHjWJYTUQk
pjx9j8k3EaZZ4qGrJJIjJ5D0QFhxXJKjGd+4P6U4QOYJIHh/dKBxh5xKQtGEwYGI
eV4CMqII3F8qx8DJQrNfx8DGJ5eRg9YcYYI6jYHvOw5rAJsR8IvBqS+HKbUvZhkC
gYA=
-----END RSA PRIVATE KEY-----"""

public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv5GICUgxFvFHKM4PMnkx
uQz4mH4eYuXG4nKdYi7Tqw9A7IxrTJqAljc5fL4h1QEbZqGRwvXkFGzY1cXY0+Y8
/L2jzaJK1L9R5RVLp7r2PD1M5XrDXoXHHpJ5KiXuKFPqD1vvXCEaUhwh3gXy94fP
XutxqDZhKXBqXPDovz8ZTzAPs2ruf1j7Kz4gZj3YJyV4HvT9n4bAn9tZ0wKxX5Zk
OvwJHU+FoY0ARDYa1HdIH4WP92BjYYD1yGJXBP+okQtQGPyJbFZwbBLcHqY0pIGJ
HPly9UQZHxh1jFm0MsEFhXxuqhD6UNS0AJUzGZqQG6sKxH3I7M4Vc3DyKZXPjwpX
NQIDAQAB
-----END PUBLIC KEY-----"""
