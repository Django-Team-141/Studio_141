from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        # اعلان تلگرام برای درخواست جدید اینجا وصل می‌شود
        from . import signals  # noqa: F401