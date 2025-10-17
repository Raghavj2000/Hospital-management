import json
from functools import wraps
from flask import request
from app import redis_client

def cache_key_from_request(prefix, *args, **kwargs):
    """Generate cache key from request parameters"""
    params = request.args.to_dict()
    params_str = json.dumps(params, sort_keys=True)
    return f"{prefix}:{params_str}"

def cache_response(prefix, timeout=300):
    """Decorator to cache API responses"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not redis_client:
                return fn(*args, **kwargs)

            # Generate cache key
            cache_key = cache_key_from_request(prefix)

            # Try to get from cache
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                print(f"Cache read error: {e}")

            # Call the function
            response = fn(*args, **kwargs)

            # Cache the response
            try:
                redis_client.setex(cache_key, timeout, json.dumps(response))
            except Exception as e:
                print(f"Cache write error: {e}")

            return response
        return wrapper
    return decorator

def invalidate_cache(pattern):
    """Invalidate cache keys matching pattern"""
    if not redis_client:
        return

    try:
        keys = redis_client.keys(f"{pattern}*")
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        print(f"Cache invalidation error: {e}")

def set_cache(key, value, timeout=300):
    """Set a cache value"""
    if not redis_client:
        return

    try:
        redis_client.setex(key, timeout, json.dumps(value))
    except Exception as e:
        print(f"Cache set error: {e}")

def get_cache(key):
    """Get a cache value"""
    if not redis_client:
        return None

    try:
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
    except Exception as e:
        print(f"Cache get error: {e}")

    return None
