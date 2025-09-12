"""
Cache management utilities for monitoring, maintenance, and optimization
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import redis.asyncio as aioredis
from fastapi_cache import FastAPICache

logger = logging.getLogger(__name__)


class CacheManager:
    """Utility class for cache management and monitoring"""
    
    def __init__(self):
        self.redis_read: Optional[aioredis.Redis] = None
        self.redis_write: Optional[aioredis.Redis] = None
    
    def _get_redis_connections(self):
        """Get Redis connections from FastAPICache"""
        if not self.redis_read or not self.redis_write:
            backend = FastAPICache.get_backend()
            self.redis_read = backend.redis
            self.redis_write = backend.redis
        return self.redis_read, self.redis_write
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """Get comprehensive cache information"""
        try:
            redis_read, redis_write = self._get_redis_connections()
            
            # Get Redis info
            info = await redis_read.info()
            
            # Get key statistics
            key_stats = await self._get_key_statistics()
            
            # Calculate cache efficiency
            keyspace_hits = info.get('keyspace_hits', 0)
            keyspace_misses = info.get('keyspace_misses', 0)
            total_requests = keyspace_hits + keyspace_misses
            hit_ratio = keyspace_hits / total_requests if total_requests > 0 else 0
            
            return {
                "redis_info": {
                    "version": info.get('redis_version'),
                    "used_memory": info.get('used_memory_human'),
                    "used_memory_peak": info.get('used_memory_peak_human'),
                    "connected_clients": info.get('connected_clients'),
                    "total_commands_processed": info.get('total_commands_processed'),
                    "keyspace_hits": keyspace_hits,
                    "keyspace_misses": keyspace_misses,
                    "hit_ratio": round(hit_ratio * 100, 2)
                },
                "key_statistics": key_stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {"error": str(e)}
    
    async def _get_key_statistics(self) -> Dict[str, Any]:
        """Get statistics about cached keys"""
        try:
            redis_read, _ = self._get_redis_connections()
            
            # Get all keys (be careful in production with large datasets)
            all_keys = await redis_read.keys("*")
            
            # Categorize keys by prefix
            key_categories = {}
            total_keys = len(all_keys)
            
            for key in all_keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                prefix = key_str.split(':')[0] if ':' in key_str else 'other'
                
                if prefix not in key_categories:
                    key_categories[prefix] = 0
                key_categories[prefix] += 1
            
            return {
                "total_keys": total_keys,
                "categories": key_categories
            }
        except Exception as e:
            logger.error(f"Error getting key statistics: {e}")
            return {"error": str(e)}
    
    async def clear_cache_by_pattern(self, pattern: str) -> int:
        """Clear cache keys matching a pattern"""
        try:
            redis_read, redis_write = self._get_redis_connections()
            
            keys = await redis_read.keys(pattern)
            if keys:
                deleted_count = await redis_write.delete(*keys)
                logger.info(f"Deleted {deleted_count} cache keys matching pattern: {pattern}")
                return deleted_count
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache by pattern {pattern}: {e}")
            return 0
    
    async def clear_expired_keys(self) -> int:
        """Force cleanup of expired keys"""
        try:
            redis_read, redis_write = self._get_redis_connections()
            
            # Get all keys and check their TTL
            all_keys = await redis_read.keys("*")
            expired_keys = []
            
            for key in all_keys:
                ttl = await redis_read.ttl(key)
                if ttl == -2:  # Key doesn't exist (expired)
                    expired_keys.append(key)
            
            if expired_keys:
                deleted_count = await redis_write.delete(*expired_keys)
                logger.info(f"Cleaned up {deleted_count} expired keys")
                return deleted_count
            return 0
        except Exception as e:
            logger.error(f"Error cleaning expired keys: {e}")
            return 0
    
    async def get_cache_key_details(self, key: str) -> Dict[str, Any]:
        """Get detailed information about a specific cache key"""
        try:
            redis_read, _ = self._get_redis_connections()
            
            # Check if key exists
            exists = await redis_read.exists(key)
            if not exists:
                return {"error": "Key not found"}
            
            # Get key info
            ttl = await redis_read.ttl(key)
            key_type = await redis_read.type(key)
            memory_usage = await redis_read.memory_usage(key)
            
            # Get value (be careful with large values)
            value = await redis_read.get(key)
            
            result = {
                "key": key,
                "type": key_type.decode() if isinstance(key_type, bytes) else key_type,
                "ttl": ttl,
                "memory_usage": memory_usage,
                "exists": bool(exists)
            }
            
            # Try to parse value as JSON for better display
            if value:
                try:
                    parsed_value = json.loads(value)
                    result["value"] = parsed_value
                    result["value_size"] = len(value)
                except json.JSONDecodeError:
                    result["value"] = value.decode() if isinstance(value, bytes) else str(value)
                    result["value_size"] = len(str(value))
            
            return result
        except Exception as e:
            logger.error(f"Error getting cache key details for {key}: {e}")
            return {"error": str(e)}
    
    async def optimize_cache(self) -> Dict[str, Any]:
        """Perform cache optimization tasks"""
        results = {}
        
        try:
            # Clear expired keys
            expired_count = await self.clear_expired_keys()
            results["expired_keys_cleared"] = expired_count
            
            # Get memory info before and after
            redis_read, _ = self._get_redis_connections()
            info_after = await redis_read.info()
            results["memory_after_cleanup"] = info_after.get('used_memory_human')
            
            logger.info(f"Cache optimization completed: {results}")
            return results
        except Exception as e:
            logger.error(f"Error during cache optimization: {e}")
            return {"error": str(e)}
    
    async def monitor_cache_health(self) -> Dict[str, Any]:
        """Monitor cache health and return recommendations"""
        try:
            cache_info = await self.get_cache_info()
            redis_info = cache_info.get("redis_info", {})
            
            recommendations = []
            health_score = 100
            
            # Check hit ratio
            hit_ratio = redis_info.get("hit_ratio", 0)
            if hit_ratio < 50:
                recommendations.append("Low cache hit ratio. Consider warming cache or adjusting TTL values.")
                health_score -= 20
            elif hit_ratio < 70:
                recommendations.append("Moderate cache hit ratio. Monitor cache usage patterns.")
                health_score -= 10
            
            # Check memory usage (this would need Redis maxmemory info)
            # For now, we'll use a simple heuristic
            total_keys = cache_info.get("key_statistics", {}).get("total_keys", 0)
            if total_keys > 100000:
                recommendations.append("High number of cache keys. Consider implementing key expiration policies.")
                health_score -= 15
            
            # Check connected clients
            connected_clients = redis_info.get("connected_clients", 0)
            if connected_clients > 100:
                recommendations.append("High number of Redis connections. Monitor connection pooling.")
                health_score -= 10
            
            if not recommendations:
                recommendations.append("Cache is performing well.")
            
            return {
                "health_score": max(0, health_score),
                "recommendations": recommendations,
                "cache_info": cache_info
            }
        except Exception as e:
            logger.error(f"Error monitoring cache health: {e}")
            return {"error": str(e), "health_score": 0}


# Global cache manager instance
cache_manager = CacheManager()


async def schedule_cache_maintenance(interval_hours: int = 6):
    """Schedule periodic cache maintenance"""
    while True:
        try:
            logger.info("Starting scheduled cache maintenance...")
            results = await cache_manager.optimize_cache()
            logger.info(f"Cache maintenance completed: {results}")
            
            # Wait for next interval
            await asyncio.sleep(interval_hours * 3600)
            
        except Exception as e:
            logger.error(f"Error in scheduled cache maintenance: {e}")
            # Wait before retrying
            await asyncio.sleep(3600)  # 1 hour
