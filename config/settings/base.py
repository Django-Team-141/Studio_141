from pathlib import Path

import environ

# config/settings/base.py ← سه پوشه بالاتر، ریشه‌ی پروژه است
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

ADMIN_URL = env("ADMIN_URL", default="admin/")
# فقط وقتی پشت پروکسی خودمان (Caddy) هستیم True می‌شود
TRUST_PROXY = env.bool("TRUST_PROXY", default=False)

INSTALLED_APPS = [
    "core.adminconfig.OTPAdminConfig",  # ادمین جنگو، با ورود دومرحله‌ای
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "core",
    "portfolio",
    "plans",
    "orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "core.middleware.SecurityHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_language",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# دیتابیس پیش‌فرض برای کار روی سیستم خودتان. در prod.py با Postgres عوض می‌شود.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# کش مشترک بین همه‌ی پروسه‌ها (محدودیت فرم و قفل لاگین ادمین از اینجا می‌خوانند).
# جدولش با: python manage.py createcachetable ساخته می‌شود.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

AUTHENTICATION_BACKENDS = ["core.lockout.LockoutBackend"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 15},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

LANGUAGE_CODE = "fa"
LANGUAGES = [("fa", "Persian"), ("en", "English")]
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- ورود دومرحله‌ای (2FA) ---
OTP_TOTP_ISSUER = "141 Studio"

# --- دکمه‌های تماس ثابت ---
# اگر در ادمین (Site settings) مقدار داده شود، آن مقدار برنده است.
# این‌ها فقط جایگزین‌اند، وقتی در ادمین خالی باشد.
CONTACT_TELEGRAM = env("CONTACT_TELEGRAM", default="")
CONTACT_WHATSAPP = env("CONTACT_WHATSAPP", default="")
CONTACT_INSTAGRAM = env("CONTACT_INSTAGRAM", default="")

# --- اعلان تلگرام برای درخواست جدید ---
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID", default="")
# False یعنی پیام تلگرام فقط کد، پلن و شماره‌ی ماسک‌شده دارد (نام و شماره‌ی کامل به تلگرام نمی‌رود)
TELEGRAM_FULL_DETAILS = env.bool("TELEGRAM_FULL_DETAILS", default=False)
TELEGRAM_API_BASE = env("TELEGRAM_API_BASE", default="https://api.telegram.org")

# --- امنیت (مشترک؛ بخش‌های فقط‌سرور در prod.py است) ---
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
# بعد از ۳۰ دقیقه بی‌کاری نشست تمام می‌شود (ادمین دوباره باید وارد شود)
SESSION_COOKIE_AGE = 30 * 60
SESSION_SAVE_EVERY_REQUEST = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "security": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "orders": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}