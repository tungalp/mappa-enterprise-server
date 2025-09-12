# http_client.py
import httpx
from httpx import AsyncClient, Timeout
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

# Global client instance
_global_client: Optional[AsyncClient] = None
_client_lock = asyncio.Lock()

async def get_global_client() -> AsyncClient:
    """
    Get or create the global async client with thread-safe initialization
    """
    global _global_client
    
    if _global_client is None:
        async with _client_lock:
            # Double-checked locking pattern
            if _global_client is None:
                _global_client = AsyncClient(
                    timeout=Timeout(15.0, connect=3.0),
                    limits=httpx.Limits(
                        max_keepalive_connections=100,
                        max_connections=200,
                        keepalive_expiry=60.0
                    ),
                    transport=httpx.AsyncHTTPTransport(
                        retries=2
                    ),
                    verify=False,
                    follow_redirects=True
                )
                logger.info("Global HTTP client initialized")
    
    return _global_client

async def close_global_client():
    """Close the global client gracefully"""
    global _global_client
    
    if _global_client:
        await _global_client.aclose()
        _global_client = None
        logger.info("Global HTTP client closed")
