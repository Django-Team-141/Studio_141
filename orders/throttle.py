from django.core.cache import cache


def allow(key, limit, window):
    """True اگر هنوز به سقف تعداد در بازه‌ی window (ثانیه) نرسیده باشد."""
    cache.add(key, 0, timeout=window)
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=window)
        count = 1
    return count <= limit