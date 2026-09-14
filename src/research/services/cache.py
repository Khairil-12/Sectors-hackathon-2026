from django.core.cache import cache


CACHE_TTLS = {
    "daily": 900,
    "company": 86400,
    "quarterly": 86400,
    "broker": 900,
    "news": 1800,
    "screener": 300,
}


def cache_key(prefix: str, params: dict) -> str:
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v)
    return f"sectors:{prefix}:{sorted_params}"


def get_or_set(key: str, fetch_fn, ttl_key: str = "daily"):
    cached = cache.get(key)
    if cached is not None:
        return cached
    data = fetch_fn()
    cache.set(key, data, CACHE_TTLS.get(ttl_key, 300))
    return data
