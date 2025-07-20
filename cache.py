"""
Caching system for the Financial Valuation Engine

This module provides caching functionality for expensive calculations
to improve performance and reduce redundant computations.
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
import threading

from logging_config import get_logger

logger = get_logger(__name__)

class ValuationCache:
    """
    Cache for expensive valuation calculations.
    
    This cache stores results of expensive calculations to avoid
    recomputing them when the same inputs are provided.
    """
    
    def __init__(self, max_size: int = 128, ttl_seconds: Optional[int] = None):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items in cache
            ttl_seconds: Time to live for cache entries (None = no expiration)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._access_times: Dict[str, float] = {}
    
    def _generate_key(self, func_name: str, *args, **kwargs) -> str:
        """
        Generate a cache key from function name and arguments.
        
        Args:
            func_name: Name of the function
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a serializable representation of arguments
        key_data = {
            'func_name': func_name,
            'args': args,
            'kwargs': kwargs
        }
        
        # Convert to JSON string and hash it
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """
        Check if a cache entry has expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if expired, False otherwise
        """
        if self.ttl_seconds is None:
            return False
        
        if key not in self._access_times:
            return True
        
        return time.time() - self._access_times[key] > self.ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            if self._is_expired(key):
                self._remove(key)
                return None
            
            # Update access time
            self._access_times[key] = time.time()
            return self._cache[key]['value']
    
    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            # Remove oldest entry if cache is full
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            self._cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
            self._access_times[key] = time.time()
            
            logger.debug(f"Cached result for key: {key[:8]}...")
    
    def _remove(self, key: str) -> None:
        """
        Remove an entry from the cache.
        
        Args:
            key: Cache key to remove
        """
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
    
    def _evict_oldest(self) -> None:
        """Remove the least recently used entry from the cache."""
        if not self._access_times:
            return
        
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._remove(oldest_key)
        logger.debug(f"Evicted oldest cache entry: {oldest_key[:8]}...")
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            logger.info("Cache cleared")
    
    def size(self) -> int:
        """
        Get the current number of entries in the cache.
        
        Returns:
            Number of cache entries
        """
        with self._lock:
            return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds,
                'utilization': len(self._cache) / self.max_size if self.max_size > 0 else 0
            }

# Global cache instance
_global_cache = ValuationCache()

def cached(func: Callable) -> Callable:
    """
    Decorator to cache function results.
    
    Args:
        func: Function to cache
        
    Returns:
        Wrapped function with caching
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key
        key = _global_cache._generate_key(func.__name__, *args, **kwargs)
        
        # Try to get from cache
        cached_result = _global_cache.get(key)
        if cached_result is not None:
            logger.debug(f"Cache hit for {func.__name__}")
            return cached_result
        
        # Compute result and cache it
        logger.debug(f"Cache miss for {func.__name__}, computing...")
        result = func(*args, **kwargs)
        _global_cache.set(key, result)
        
        return result
    
    return wrapper

def cached_with_params(max_size: int = 128, ttl_seconds: Optional[int] = None):
    """
    Decorator factory for caching with custom parameters.
    
    Args:
        max_size: Maximum cache size
        ttl_seconds: Time to live for cache entries
        
    Returns:
        Caching decorator
    """
    cache = ValuationCache(max_size=max_size, ttl_seconds=ttl_seconds)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = cache._generate_key(func.__name__, *args, **kwargs)
            
            cached_result = cache.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            logger.debug(f"Cache miss for {func.__name__}, computing...")
            result = func(*args, **kwargs)
            cache.set(key, result)
            
            return result
        
        return wrapper
    
    return decorator

def clear_cache() -> None:
    """Clear the global cache."""
    _global_cache.clear()

def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics for the global cache.
    
    Returns:
        Cache statistics
    """
    return _global_cache.stats()

# Specialized caches for different calculation types
dcf_cache = ValuationCache(max_size=64, ttl_seconds=3600)  # 1 hour TTL
monte_carlo_cache = ValuationCache(max_size=32, ttl_seconds=1800)  # 30 min TTL
sensitivity_cache = ValuationCache(max_size=48, ttl_seconds=7200)  # 2 hour TTL

def cache_dcf_result(params_hash: str, result: Any) -> None:
    """
    Cache a DCF calculation result.
    
    Args:
        params_hash: Hash of the parameters used
        result: Calculation result to cache
    """
    dcf_cache.set(params_hash, result)

def get_cached_dcf_result(params_hash: str) -> Optional[Any]:
    """
    Get a cached DCF calculation result.
    
    Args:
        params_hash: Hash of the parameters used
        
    Returns:
        Cached result or None
    """
    return dcf_cache.get(params_hash)

def cache_monte_carlo_result(params_hash: str, result: Any) -> None:
    """
    Cache a Monte Carlo simulation result.
    
    Args:
        params_hash: Hash of the parameters used
        result: Simulation result to cache
    """
    monte_carlo_cache.set(params_hash, result)

def get_cached_monte_carlo_result(params_hash: str) -> Optional[Any]:
    """
    Get a cached Monte Carlo simulation result.
    
    Args:
        params_hash: Hash of the parameters used
        
    Returns:
        Cached result or None
    """
    return monte_carlo_cache.get(params_hash) 