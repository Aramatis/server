from django.core.cache import cache

import hashlib


def cache_get_key(*args, **kwargs):
    """
    Get the cache key for storage
    :param args: function args
    :param kwargs: function kwgars
    :return: key in cache
    """
    serialise = []
    for arg in args:
        serialise.append(str(arg))
    for key, arg in kwargs.items():
        serialise.append(str(key))
        serialise.append(str(arg))
    key = hashlib.md5("".join(serialise)).hexdigest()
    return key


def cache_for(time):
    """
    Decorator for caching functions
    :param time: time to live
    :return: function value (cached value if exists)
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            key = cache_get_key(fn.__name__, *args, **kwargs)
            result = cache.get(key)
            if not result:
                result = fn(*args, **kwargs)
                cache.set(key, result, timeout=time)
            return result

        return wrapper

    return decorator
