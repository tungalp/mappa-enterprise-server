"""
Cache metrics tracking module - separate from cache_warmer to avoid circular imports
"""
from typing import Dict, Any


class CacheMetrics:
    """Track cache performance metrics"""
    
    def __init__(self):
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_errors = 0
    
    def record_hit(self):
        self.cache_hits += 1
    
    def record_miss(self):
        self.cache_misses += 1
    
    def record_error(self):
        self.cache_errors += 1
    
    def get_hit_ratio(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_errors": self.cache_errors,
            "hit_ratio": self.get_hit_ratio()
        }
    
    def reset(self):
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_errors = 0


# Global metrics instance
cache_metrics = CacheMetrics()
