from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Annotated, Callable, Optional, Any, Dict, List
from enum import Enum
import uuid
import jwt
from datetime import datetime, timedelta, timezone
import string
import secrets
from passlib.context import CryptContext
from dependency_injector.wiring import Provide, inject

from desktop_mobile.models.entities import (
    ApiKeyEntity,
    ApiKeyPermissionEntity,
    CollectionEntity,
    MapEntity,
    LayerEntity,
    collection_map,
    map_layer
)
from desktop_mobile.models.schemas import UserPrincipal

# Cryptographic password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Authorization Constants
class ResourceType(str, Enum):
    COLLECTION = "collection"
    MAP = "map"
    LAYER = "layer"

class ResourceAccess(str, Enum):
    ADMIN = "admin"
    USER = "user"

KEY_PREFIX = "pk_"
KEY_SUFFIX_LENGTH = 29
ALLOWED_CHARS = string.ascii_letters + string.digits + '-_'
KEY_LENGTH = 32
KEY_PREFIX_LENGTH = 15

TOKEN_EXPIRATION_MINUTES = 60
SECRET_KEY = "Mapa_QGIS_Secret_Key"
ALGORITHM = "HS256"

# Helper dependency to yield DB session from Container
@inject
async def get_db_session(db = Depends(Provide["db"])):
    # Since "db" is registered as a provider name in the container,
    # dependency-injector will resolve it dynamically without import-time circular dependency.
    async with db.session() as session:
        yield session

def generate_prefixed_key() -> str:
    """Generates a raw API key string starting with 'pk_'."""
    suffix = ''.join(secrets.choice(ALLOWED_CHARS) for _ in range(KEY_SUFFIX_LENGTH))
    return KEY_PREFIX + suffix

def generate_key_data() -> tuple[str, str, str]:
    """Generates raw secret key, public ID, and hash."""
    raw_key = generate_prefixed_key()
    public_lookup_id = raw_key[:KEY_PREFIX_LENGTH]
    hashed_key = pwd_context.hash(raw_key)
    return raw_key, public_lookup_id, hashed_key

def create_jwt(user_id: uuid.UUID, public_lookup_id: str, duration_minutes: int, tenant_id: Optional[str] = None) -> tuple[str, datetime]:
    """Creates a cryptographically signed short-lived JWT."""
    now = datetime.now(timezone.utc)
    expiration_time = now + timedelta(minutes=duration_minutes)
    
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "lok": str(public_lookup_id),
        "exp": int(expiration_time.timestamp()),
        "iat": int(now.timestamp()),
        "tenant_id": tenant_id
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expiration_time

def decode_jwt(token: str) -> Dict[str, Any]:
    """Decodes and verifies a JWT."""
    return jwt.decode(
        token, 
        SECRET_KEY, 
        algorithms=[ALGORITHM],
        options={"verify_signature": True, "verify_exp": True}
    )

def get_raw_token(
    authorization: Annotated[Optional[str], Header(alias="Authorization")] = None
) -> str:
    """Extracts raw token string from the Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be provided in 'Bearer <token>' format."
        )
    return authorization.split(" ")[1]

def get_verified_token_principal(
    raw_token: Annotated[str, Depends(get_raw_token)]
) -> UserPrincipal:
    """Cryptographically verifies JWT signature and returns UserPrincipal."""
    try:
        payload = decode_jwt(raw_token)
        apikey_id_str = payload.get("sub")
        public_lookup_id = payload.get("lok")

        if not apikey_id_str or not public_lookup_id:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing required claims."
             )
             
        return UserPrincipal(
            id=uuid.UUID(apikey_id_str),
            public_lookup_id=public_lookup_id
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please re-authenticate."
        )
    except (jwt.InvalidSignatureError, jwt.DecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT signature or structure."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed during token processing."
        )

def get_api_key_header(
    authorization: Annotated[Optional[str], Header(alias="Authorization")] = None
) -> str:
    """Extracts raw API key string from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be provided in 'Bearer pk_...' format."
        )
    
    raw_key = authorization.split(" ")[1]
    
    if not (raw_key.startswith(KEY_PREFIX) and len(raw_key) == KEY_LENGTH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid key format or length. Expected {KEY_LENGTH} characters starting with '{KEY_PREFIX}'."
        )

    return raw_key

async def get_verified_api_key(
    raw_key: Annotated[str, Depends(get_api_key_header)],
    db: Annotated[AsyncSession, Depends(get_db_session)]
) -> ApiKeyEntity:
    """Performs database lookup and verification of the long-lived API key."""
    lookup_id = raw_key[:KEY_PREFIX_LENGTH]
    
    stmt = select(ApiKeyEntity).where(
        ApiKeyEntity.public_lookup_id == lookup_id,
        ApiKeyEntity.is_active == True
    )
    result = await db.execute(stmt)
    api_key_record = result.scalars().first()
    
    if not api_key_record or not pwd_context.verify(raw_key, api_key_record.hashed_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key."
        )
        
    return api_key_record

def determine_target_id(
    target_id: Optional[uuid.UUID],
    collection_id: Optional[uuid.UUID],
    map_id: Optional[uuid.UUID],
    layer_id: Optional[uuid.UUID],
    resource: ResourceType
) -> Optional[uuid.UUID]:
    """Determine the actual target ID using cascading priority rules."""
    if target_id is not None:
        return target_id
    
    if resource == ResourceType.COLLECTION and collection_id is not None:
        return collection_id
    elif resource == ResourceType.MAP and map_id is not None:
        return map_id
    elif resource == ResourceType.LAYER and layer_id is not None:
        return layer_id
    
    return None

def check_permission(action: ResourceAccess, resource: ResourceType) -> Callable:
    """
    Factory dependency verifying cascading authorization across GIS resources.
    Looks up specific permissions on Collection, Map, or Layer or checks for global admin keys.
    """
    async def permission_checker(
        target_id: Optional[uuid.UUID] = None,
        collection_id: Optional[uuid.UUID] = None,
        map_id: Optional[uuid.UUID] = None,
        layer_id: Optional[uuid.UUID] = None,
        verified_principal: UserPrincipal = Depends(get_verified_token_principal),
        db: AsyncSession = Depends(get_db_session)
    ):
        actual_target_id = determine_target_id(
            target_id=target_id,
            collection_id=collection_id,
            map_id=map_id, 
            layer_id=layer_id,
            resource=resource
        )

        # Define Required Access Levels
        action_list = [action.value]
        if action.value == ResourceAccess.USER.value:
            action_list.append(ResourceAccess.ADMIN.value)
        
        permission_filter = None
        
        # Build Cascade Permission Filter
        if resource == ResourceType.COLLECTION and actual_target_id:
            # Find Collection existence
            c_stmt = select(CollectionEntity.id).where(CollectionEntity.id == actual_target_id)
            res = await db.execute(c_stmt)
            if not res.scalars().first():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found.")

            permission_filter = or_(
                ApiKeyPermissionEntity.target_collection_id == actual_target_id
            )
            
        elif resource == ResourceType.MAP and actual_target_id:
            # Find Map existence
            m_stmt = select(MapEntity.id).where(MapEntity.id == actual_target_id)
            res = await db.execute(m_stmt)
            if not res.scalars().first():
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found.")

            # Find Parent Collection ID for cascading access
            col_stmt = select(collection_map.c.collection_id).where(
                collection_map.c.map_id == actual_target_id
            )
            res = await db.execute(col_stmt)
            parent_collection_id = res.scalars().first()
            
            permission_filter = or_(
                ApiKeyPermissionEntity.target_map_id == actual_target_id
            )
            if parent_collection_id:
                permission_filter = or_(
                    permission_filter,
                    ApiKeyPermissionEntity.target_collection_id == parent_collection_id
                )

        elif resource == ResourceType.LAYER and actual_target_id:
            # Find Layer existence
            l_stmt = select(LayerEntity.id).where(LayerEntity.id == actual_target_id)
            res = await db.execute(l_stmt)
            if not res.scalars().first():
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer not found.")
            
            # Find Parent Map ID
            map_stmt = select(map_layer.c.map_id).where(
                map_layer.c.layer_id == actual_target_id
            )
            res = await db.execute(map_stmt)
            parent_map_id = res.scalars().first()
            
            permission_filter = or_(
                ApiKeyPermissionEntity.target_layer_id == actual_target_id
            )
            if parent_map_id:
                permission_filter = or_(
                    permission_filter,
                    ApiKeyPermissionEntity.target_map_id == parent_map_id
                )

        # Global Permission filter (targets are NULL means global access)
        global_filter = and_(
            ApiKeyPermissionEntity.target_collection_id.is_(None),
            ApiKeyPermissionEntity.target_map_id.is_(None),
            ApiKeyPermissionEntity.target_layer_id.is_(None)
        )

        if permission_filter is None:
            permission_filter = global_filter
        else:
            permission_filter = or_(permission_filter, global_filter)

        # Query DB for matching permission
        perm_stmt = select(ApiKeyPermissionEntity).where(
            ApiKeyPermissionEntity.apikey_id == verified_principal.id,
            permission_filter,
            ApiKeyPermissionEntity.access_level.in_(action_list)
        )
        perm_res = await db.execute(perm_stmt)
        has_permission = perm_res.scalars().first()

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API Key lacks required '{action.value}' permission for resource type '{resource.value}:{actual_target_id}'."
            )
        return verified_principal

    return permission_checker
