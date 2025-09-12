"""
Cache package for service performance optimization

This package provides comprehensive caching functionality including:
- Redis-based caching for database operations
- Performance monitoring and metrics
- Configurable cache strategies
"""

from .cache_config import CacheConfig, get_cache_config_from_env, get_cache_strategy
from .cache_metrics import cache_metrics
from .cache_manager import CacheManager, cache_manager

__all__ = [
    "CacheConfig",
    "get_cache_config_from_env",
    "get_cache_strategy",
    "cache_metrics",
    "CacheManager",
    "cache_manager"
]
