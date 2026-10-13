from .base import *  # noqa: F401,F403

# فقط برای تست‌ها و CI. از فایل .env هیچ چیزی نمی‌خواند و به شبکه وصل نمی‌شود.
SECRET_KEY = "test-only-not-a-real-key"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = []
ADMIN_URL = "panel-test/"
TRUST_PROXY = False

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# هش سریع، چون تست‌ها دهها کاربر می‌سازند
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# مقدارهای .env شما نباید روی نتیجه‌ی تست اثر بگذارد
CONTACT_TELEGRAM = ""
CONTACT_EMAIL = ""
CONTACT_WHATSAPP = ""
CONTACT_INSTAGRAM = ""
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
TELEGRAM_CHAT_ID_2 = ""
TELEGRAM_CHAT_ID_3 = ""
TELEGRAM_CHAT_ID_4 = ""
TELEGRAM_FULL_DETAILS = False
EMAIL_HOST = ""
ORDER_NOTIFY_EMAIL_TO = []