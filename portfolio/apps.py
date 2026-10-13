from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portfolio"

    def ready(self):
        # پاک شدن فایل‌های قدیمی (عکس و ویدیو) اینجا وصل می‌شود
        from . import signals  # noqa: F401