from django.conf import settings

# فونت‌ها از خود سایت می‌آیند، پس به Google Fonts دیگر اجازه‌ای نمی‌دهیم
CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "font-src 'self'; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'"
)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/" + settings.ADMIN_URL):
            # پنل ادمین قالب‌های خودش را دارد، پس CSP برایش نمی‌گذاریم؛ ولی در گوگل هم نباید بیاید
            response.headers.setdefault("X-Robots-Tag", "noindex, nofollow")
        else:
            response.headers.setdefault("Content-Security-Policy", CSP)
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        return response