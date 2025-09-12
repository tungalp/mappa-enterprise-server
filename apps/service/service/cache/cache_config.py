"""
Cache configuration settings
"""
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class CacheConfig:
    """Cache configuration settings"""
    
    # TTL settings (in seconds)
    tenant_ttl: int = 300  # 5 minutes
    api_ttl: int = 180     # 3 minutes
    api_details_ttl: int = 120  # 2 minutes
    
    # Default TTL for general caching
    default_ttl: int = 300  # Default 5 minutes TTL
    
    # Maintenance settings
    maintenance_interval: int = 6  # hours
    auto_cleanup_expired: bool = True
    
    # Performance settings
    enable_metrics: bool = True


# Default cache configuration
DEFAULT_CACHE_CONFIG = CacheConfig()


def get_cache_config_from_env() -> CacheConfig:
    """Get cache configuration from environment variables"""
    import os
    
    config = CacheConfig()
    
    # TTL settings
    config.tenant_ttl = int(os.getenv("CACHE_TENANT_TTL", config.tenant_ttl))
    config.api_ttl = int(os.getenv("CACHE_API_TTL", config.api_ttl))
    config.api_details_ttl = int(os.getenv("CACHE_API_DETAILS_TTL", config.api_details_ttl))
    
    # General settings
    config.default_ttl = int(os.getenv("CACHE_DEFAULT_TTL", config.default_ttl))
    

    
    # Maintenance settings
    config.maintenance_interval = int(os.getenv("CACHE_MAINTENANCE_INTERVAL", config.maintenance_interval))
    config.auto_cleanup_expired = os.getenv("CACHE_AUTO_CLEANUP", "true").lower() == "true"
    
    # Performance settings
    config.enable_metrics = os.getenv("CACHE_ENABLE_METRICS", "true").lower() == "true"
    
    return config


def get_cache_recommendations(cache_info: Dict[str, Any]) -> list:
    """Generate cache optimization recommendations based on current state"""
    recommendations = []
    
    redis_info = cache_info.get("redis_info", {})
    key_stats = cache_info.get("key_statistics", {})
    
    # Check hit ratio
    hit_ratio = redis_info.get("hit_ratio", 0)
    if hit_ratio < 50:
        recommendations.append({
            "type": "performance",
            "priority": "high",
            "message": "Cache hit ratio is below 50%. Consider adjusting TTL values or reviewing cache key patterns.",
            "action": "adjust_ttl"
        })
    elif hit_ratio < 70:
        recommendations.append({
            "type": "performance",
            "priority": "medium",
            "message": "Cache hit ratio could be improved. Monitor cache usage patterns.",
            "action": "monitor"
        })
    
    # Check key count
    total_keys = key_stats.get("total_keys", 0)
    if total_keys > 100000:
        recommendations.append({
            "type": "memory",
            "priority": "medium", 
            "message": "High number of cache keys detected. Consider implementing key expiration policies.",
            "action": "optimize_expiration"
        })
    elif total_keys < 1000:
        recommendations.append({
            "type": "utilization",
            "priority": "low",
            "message": "Low cache utilization. Monitor application usage patterns.",
            "action": "monitor"
        })
    
    # Check memory usage patterns
    categories = key_stats.get("categories", {})
    if len(categories) > 10:
        recommendations.append({
            "type": "organization",
            "priority": "low",
            "message": "Many different cache key categories. Consider consolidating cache strategies.",
            "action": "consolidate"
        })
    
    # Check for imbalanced categories
    if categories:
        max_category_count = max(categories.values())
        min_category_count = min(categories.values())
        if max_category_count > min_category_count * 10:
            recommendations.append({
                "type": "balance",
                "priority": "medium",
                "message": "Imbalanced cache usage across categories. Some data types may need different TTL values.",
                "action": "adjust_ttl"
            })
    
    return recommendations


# Cache strategy templates for different use cases
CACHE_STRATEGIES = {
    "high_traffic": CacheConfig(
        tenant_ttl=600,  # 10 minutes
        api_ttl=300,     # 5 minutes
        api_details_ttl=180,  # 3 minutes
    ),

    "low_latency": CacheConfig(
        tenant_ttl=900,  # 15 minutes
        api_ttl=600,     # 10 minutes
        api_details_ttl=300,  # 5 minutes
    ),

    "memory_optimized": CacheConfig(
        tenant_ttl=180,  # 3 minutes
        api_ttl=120,     # 2 minutes
        api_details_ttl=60,   # 1 minute
        maintenance_interval=2
    ),

    "development": CacheConfig(
        tenant_ttl=60,   # 1 minute
        api_ttl=30,      # 30 seconds
        api_details_ttl=15,   # 15 seconds
        maintenance_interval=1
    )
}


def get_cache_strategy(strategy_name: str) -> CacheConfig:
    """Get a predefined cache strategy configuration"""
    return CACHE_STRATEGIES.get(strategy_name, DEFAULT_CACHE_CONFIG)


