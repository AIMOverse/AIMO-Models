import os
from typing import Optional
import redis
from redis.connection import ConnectionPool
from redis.exceptions import RedisError

class RedisClient:
    """
    Redis client utility class, providing connection pool and error handling
    """
    _pool: Optional[ConnectionPool] = None
    
    @classmethod
    def get_connection_pool(cls) -> ConnectionPool:
        """Get or create Redis connection pool"""
        if cls._pool is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            cls._pool = redis.ConnectionPool.from_url(
                url=redis_url,
                decode_responses=True,
                max_connections=10
            )
        return cls._pool
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """Get Redis client connection"""
        try:
            return redis.Redis(connection_pool=cls.get_connection_pool())
        except RedisError as e:
            raise ConnectionError(f"Unable to connect to Redis: {str(e)}")
    
    @classmethod
    def close(cls) -> None:
        """Close Redis connection pool"""
        if cls._pool is not None:
            cls._pool.disconnect()
            cls._pool = None
