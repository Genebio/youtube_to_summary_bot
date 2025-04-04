import pytest
import json
from unittest.mock import patch
from utils.cache import get_cached_data, set_cached_data, cached, clear_cache, check_redis_connection

class TestCache:
    """Test class for Redis cache utility functions."""
    
    @pytest.mark.asyncio
    async def test_get_cached_data_hit(self, mock_redis_client):
        """Test retrieving data from cache when it exists."""
        mock_redis_client.get.return_value = json.dumps({"data": "test_data"}).encode()
        
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await get_cached_data("test_key")
            
            mock_redis_client.get.assert_called_once_with("test_key")
            assert result == {"data": "test_data"}
    
    @pytest.mark.asyncio
    async def test_get_cached_data_miss(self, mock_redis_client):
        """Test retrieving data from cache when it doesn't exist."""
        mock_redis_client.get.return_value = None
        
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await get_cached_data("test_key")
            
            mock_redis_client.get.assert_called_once_with("test_key")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_cached_data_error(self, mock_redis_client):
        """Test error handling when retrieving data from cache."""
        mock_redis_client.get.side_effect = Exception("Redis error")
        
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await get_cached_data("test_key")
            
            mock_redis_client.get.assert_called_once_with("test_key")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_set_cached_data_success(self, mock_redis_client):
        """Test successfully setting data in cache."""
        test_data = {"data": "test_data"}
        
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await set_cached_data("test_key", test_data, 3600)
            
            mock_redis_client.setex.assert_called_once_with("test_key", 3600, json.dumps(test_data))
            assert result is True
    
    @pytest.mark.asyncio
    async def test_set_cached_data_error(self, mock_redis_client):
        """Test error handling when setting data in cache."""
        test_data = {"data": "test_data"}
        mock_redis_client.setex.side_effect = Exception("Redis error")
        
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await set_cached_data("test_key", test_data, 3600)
            
            mock_redis_client.setex.assert_called_once_with("test_key", 3600, json.dumps(test_data))
            assert result is False
    
    @pytest.mark.asyncio
    async def test_cached_decorator_hit(self, mock_redis_client):
        """Test cached decorator when data is in cache."""
        mock_redis_client.get.return_value = json.dumps({"result": "cached_data"}).encode()
        
        @cached()
        async def test_func():
            return {"result": "original_data"}
        
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await test_func()
            
            assert mock_redis_client.get.called
            assert not mock_redis_client.setex.called
            assert result == {"result": "cached_data"}
    
    @pytest.mark.asyncio
    async def test_cached_decorator_miss(self, mock_redis_client):
        """Test cached decorator when data is not in cache."""
        mock_redis_client.get.return_value = None
        
        @cached(expiry=60)
        async def test_func():
            return {"result": "original_data"}
        
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await test_func()
            
            assert mock_redis_client.get.called
            assert mock_redis_client.setex.called
            assert result == {"result": "original_data"}
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, mock_redis_client):
        """Test clearing cache entries."""
        mock_redis_client.keys.return_value = ["key1", "key2"]
        mock_redis_client.delete.return_value = 2
        
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await clear_cache("test*")
            
            mock_redis_client.keys.assert_called_once_with("test*")
            mock_redis_client.delete.assert_called_once_with("key1", "key2")
            assert result == 2
    
    @pytest.mark.asyncio
    async def test_check_redis_connection_success(self, mock_redis_client):
        """Test successful Redis connection check."""
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await check_redis_connection()
            
            mock_redis_client.ping.assert_called_once()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_redis_connection_failure(self, mock_redis_client):
        """Test failed Redis connection check."""
        mock_redis_client.ping.side_effect = Exception("Redis error")
        
        with patch('utils.cache.redis_client', mock_redis_client):
            result = await check_redis_connection()
            
            mock_redis_client.ping.assert_called_once()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_check_redis_connection_no_client(self):
        """Test Redis connection check when no client is available."""
        with patch('utils.cache.redis_client', None):
            result = await check_redis_connection()
            assert result is False