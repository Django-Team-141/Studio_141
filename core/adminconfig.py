from django.contrib.admin.apps import AdminConfig


class OTPAdminConfig(AdminConfig):
    # مسیر به‌صورت رشته است تا فایل admin_site فقط وقتی لازم شد لود شود
    default_site = "core.admin_site.OTPAdmin"