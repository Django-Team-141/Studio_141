from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403

# روی سرور. هر چیزی که لازم است باید در .env.prod باشد، وگرنه سایت بالا نمی‌آید.
DEBUG = False

SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")
DATABASES = {"default": env.db("DATABASE_URL")}

# جلوی اشتباه‌های رایج گرفته می‌شود
if len(SECRET_KEY) < 40 or SECRET_KEY.startswith(("change-me", "django-insecure")):
    raise ImproperlyConfigured(
        "SECRET_KEY looks like a placeholder. Generate a real one: "
        "python -c \"import secrets; print(secrets.token_urlsafe(50))\""
    )
if (
    ADMIN_URL.startswith("/")
    or not ADMIN_URL.endswith("/")
    or ADMIN_URL == "admin/"
    or ADMIN_URL.startswith("choose-a-hard")
):
    raise ImproperlyConfigured(
        "ADMIN_URL must be your own hard-to-guess path, like 'k3x9-panel/' "
        "(it ends with / and does not start with /)."
    )

# کوکی‌های امن. پیشوند __Host- یعنی مرورگر فقط روی HTTPS و فقط برای همین دامنه قبولشان می‌کند.
SESSION_COOKIE_NAME = "__Host-sessionid"
CSRF_COOKIE_NAME = "__Host-csrftoken"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True
# HSTS مرحله‌به‌مرحله بالا می‌رود: اول ۳۰۰ ثانیه، بعد از اطمینان ۳۱۵۳۶۰۰۰ (یک سال)
SECURE_HSTS_SECONDS = env.int("HSTS_SECONDS", default=300)
if TRUST_PROXY:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# includeSubDomains و preload را عمداً روشن نمی‌کنیم (فقط بعد از بررسی همه‌ی ساب‌دامنه‌ها).
# این دو هشدار را ساکت می‌کنیم تا check --deploy بدون هشدار تمام شود و هر هشدار تازه دیده شود.
SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]

# اسم فایل‌های استاتیک هش می‌گیرد (مثل main.3f9a1c.css). مرورگر برای همیشه کش می‌کند
# و با هر تغییر خودکار نسخه‌ی تازه را می‌گیرد.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}