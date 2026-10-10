from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("code", "plan", "masked_phone", "status", "created_at")
    list_editable = ("status",)
    list_filter = ("status", "plan__kind")
    search_fields = ("code",)

    fields = ("code", "status", "name", "phone", "email", "plan", "message", "lang", "created_at")
    readonly_fields = ("code", "name", "phone", "email", "plan", "message", "lang", "created_at")

    # درخواست‌ها فقط از فرم سایت می‌آیند
    def has_add_permission(self, request):
        return False

    @admin.display(description="Phone")
    def masked_phone(self, obj):
        return obj.masked_phone()