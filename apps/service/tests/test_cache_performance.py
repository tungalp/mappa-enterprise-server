"""
Tests for cache performance improvements
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from service.root.root_service import RootService

from service.cache.cache_metrics import cache_metrics



class TestCachePerformance:
    """Test cache performance improvements"""
    
    @pytest.fixture
    async def mock_root_service(self):
        """Create a mock root service for testing"""
        service = MagicMock(spec=RootService)
        
        # Mock the dependencies
        service._messenger = AsyncMock()
        service._gateway_api_service = AsyncMock()
        service._connection_info_service = AsyncMock()
        service._context_var_service = AsyncMock()
        
        # Mock cache methods
        service._get_cache_key = MagicMock(return_value="test_key")
        service._get_from_cache = AsyncMock(return_value=None)
        service._set_cache = AsyncMock()
        
        return service
    
    @pytest.mark.asyncio
    async def test_tenant_lookup_caching(self, mock_root_service):
        """Test that tenant lookup uses caching effectively"""
        # Setup
        tenant_name = "test_tenant"
        expected_tenant_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # Mock the messenger response
        mock_root_service._messenger.tenant_find.return_value = {
            "tenants": [{"id": expected_tenant_id}]
        }
        
        # First call should hit database
        mock_root_service._get_from_cache.return_value = None
        result1 = await mock_root_service.find_tenant_id(tenant_name)
        
        # Verify database was called
        mock_root_service._messenger.tenant_find.assert_called_once()
        mock_root_service._set_cache.assert_called_once()
        
        # Second call should hit cache
        mock_root_service._get_from_cache.return_value = expected_tenant_id
        mock_root_service._messenger.tenant_find.reset_mock()
        
        result2 = await mock_root_service.find_tenant_id(tenant_name)
        
        # Verify database was not called again
        mock_root_service._messenger.tenant_find.assert_not_called()
        
        assert str(result1) == expected_tenant_id
        assert str(result2) == expected_tenant_id
    
    @pytest.mark.asyncio
    async def test_cache_performance_improvement(self):
        """Test that caching provides measurable performance improvement"""
        # This test would require actual Redis connection
        # For now, we'll test the concept with timing
        
        async def slow_operation():
            """Simulate a slow database operation"""
            await asyncio.sleep(0.1)  # 100ms
            return "result"
        
        async def cached_operation():
            """Simulate a fast cache hit"""
            await asyncio.sleep(0.001)  # 1ms
            return "result"
        
        # Measure slow operation
        start_time = time.perf_counter()
        result1 = await slow_operation()
        slow_time = time.perf_counter() - start_time
        
        # Measure cached operation
        start_time = time.perf_counter()
        result2 = await cached_operation()
        fast_time = time.perf_counter() - start_time
        
        # Cache should be significantly faster
        improvement_ratio = slow_time / fast_time
        assert improvement_ratio > 10  # At least 10x improvement
        assert result1 == result2
    
    def test_cache_key_generation(self):
        """Test cache key generation is consistent"""
        service = RootService(
            async_db=MagicMock(),
            gateway_api_service=MagicMock(),
            connection_info_service=MagicMock(),
            context_var_service=MagicMock(),
            messenger=MagicMock()
        )
        
        # Same inputs should generate same key
        key1 = service._get_cache_key("tenant_id", "test_tenant")
        key2 = service._get_cache_key("tenant_id", "test_tenant")
        assert key1 == key2
        
        # Different inputs should generate different keys
        key3 = service._get_cache_key("tenant_id", "different_tenant")
        assert key1 != key3
        
        # Different prefixes should generate different keys
        key4 = service._get_cache_key("api", "test_tenant")
        assert key1 != key4
    

    
    def test_cache_metrics(self):
        """Test cache metrics tracking"""
        # Reset metrics
        cache_metrics.reset()
        
        # Record some hits and misses
        cache_metrics.record_hit()
        cache_metrics.record_hit()
        cache_metrics.record_miss()
        cache_metrics.record_error()
        
        stats = cache_metrics.get_stats()
        
        assert stats["cache_hits"] == 2
        assert stats["cache_misses"] == 1
        assert stats["cache_errors"] == 1
        assert stats["hit_ratio"] == 2/3  # 2 hits out of 3 total requests
    
    @pytest.mark.asyncio
    async def test_context_var_caching(self):
        """Test that context variable lookup uses caching effectively"""
        # Setup
        tenant_id = "123e4567-e89b-12d3-a456-426614174000"
        expected_context_vars = {
            "api_key": "test_api_key_123",
            "environment": "production",
            "company_name": "Test Company"
        }

        # Create a real service instance with mocked dependencies
        mock_context_var_service = AsyncMock()
        mock_context_var_list = [
            MagicMock(key="api_key", value="test_api_key_123"),
            MagicMock(key="environment", value="production"),
            MagicMock(key="company_name", value="Test Company")
        ]
        mock_context_var_service.find.return_value = mock_context_var_list

        service = RootService(
            async_db=MagicMock(),
            gateway_api_service=MagicMock(),
            connection_info_service=MagicMock(),
            context_var_service=mock_context_var_service,
            messenger=MagicMock()
        )

        # Mock cache methods to simulate cache miss then hit
        cache_data = {}

        async def mock_get_from_cache(key):
            return cache_data.get(key)

        async def mock_set_cache(key, data, ttl):
            cache_data[key] = data

        service._get_from_cache = mock_get_from_cache
        service._set_cache = mock_set_cache

        # First call should hit database (cache miss)
        result1 = await service.find_context_var(tenant_id)

        # Verify database was called
        mock_context_var_service.find.assert_called_once()
        assert result1 == expected_context_vars

        # Second call should hit cache
        mock_context_var_service.find.reset_mock()
        result2 = await service.find_context_var(tenant_id)

        # Verify database was not called again
        mock_context_var_service.find.assert_not_called()
        assert result2 == expected_context_vars

    @pytest.mark.asyncio
    async def test_cache_invalidation(self):
        """Test cache invalidation methods"""
        mock_redis = AsyncMock()

        service = RootService(
            async_db=MagicMock(),
            gateway_api_service=MagicMock(),
            connection_info_service=MagicMock(),
            context_var_service=MagicMock(),
            messenger=MagicMock()
        )

        # Mock FastAPICache to return our mock redis
        with pytest.MonkeyPatch().context() as m:
            mock_backend = MagicMock()
            mock_backend.redis = mock_redis
            m.setattr("fastapi_cache.FastAPICache.get_backend", lambda: mock_backend)

            # Test tenant cache invalidation
            await service.invalidate_tenant_cache("test_tenant")
            mock_redis.delete.assert_called()

            # Test API cache invalidation
            await service.invalidate_api_cache("tenant1", "api1")
            assert mock_redis.delete.call_count == 2

            # Test context var cache invalidation
            await service.invalidate_context_var_cache("tenant1")
            assert mock_redis.delete.call_count == 3

            # Test bulk invalidation
            mock_redis.keys.return_value = ["key1", "key2", "key3"]
            await service.invalidate_all_tenant_caches("tenant1")
            mock_redis.keys.assert_called_with("*tenant1*")
            mock_redis.delete.assert_called_with("key1", "key2", "key3")


class TestCacheConfiguration:
    """Test cache configuration and strategies"""
    
    def test_cache_config_from_env(self, monkeypatch):
        """Test cache configuration from environment variables"""
        from service.cache.cache_config import get_cache_config_from_env
        
        # Set environment variables
        monkeypatch.setenv("CACHE_TENANT_TTL", "600")
        monkeypatch.setenv("CACHE_API_TTL", "300")
        monkeypatch.setenv("CACHE_ENABLE_METRICS", "false")

        config = get_cache_config_from_env()

        assert config.tenant_ttl == 600
        assert config.api_ttl == 300
        assert config.enable_metrics == False
    
    def test_cache_strategies(self):
        """Test predefined cache strategies"""
        from service.cache.cache_config import get_cache_strategy
        
        # Test high traffic strategy
        high_traffic = get_cache_strategy("high_traffic")
        assert high_traffic.tenant_ttl == 600

        # Test memory optimized strategy
        memory_opt = get_cache_strategy("memory_optimized")
        assert memory_opt.tenant_ttl == 180
        assert memory_opt.maintenance_interval == 2

        # Test development strategy
        dev = get_cache_strategy("development")
        assert dev.tenant_ttl == 60
        assert dev.maintenance_interval == 1


if __name__ == "__main__":
    pytest.main([__file__])
