from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # سیگنال‌های قفل لاگین اینجا ثبت می‌شوند
        from . import lockout  # noqa: F401