import os

from django.core.wsgi import get_wsgi_application

# این فایل را فقط وب‌سرور (gunicorn) روی سرور استفاده می‌کند
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()