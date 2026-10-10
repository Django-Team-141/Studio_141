from django.conf import settings


def client_ip(request):
    """IP واقعی بازدیدکننده. هدر X-Real-IP را فقط وقتی قبول می‌کنیم که پشت Caddy خودمان باشیم."""
    if settings.TRUST_PROXY:
        real = request.META.get("HTTP_X_REAL_IP", "").strip()
        if real:
            return real
    return request.META.get("REMOTE_ADDR", "")