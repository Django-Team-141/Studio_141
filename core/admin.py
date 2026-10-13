from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import FaqItem, SiteSettings, TeamMember


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Contact (shown in the contact section, the floating buttons and the footer)", {
            "fields": (
                "telegram", "email",
                "whatsapp", "whatsapp_live",
                "instagram", "instagram_live",
            ),
        }),
        ("Hero text (Persian)", {"fields": ("hero_a_fa", "hero_b_fa", "hero_sub_fa")}),
        ("Hero text (English)", {"fields": ("hero_a_en", "hero_b_en", "hero_sub_en")}),
        ("Footer and search description (Persian)", {"fields": ("footer_fa", "meta_desc_fa")}),
        ("Footer and search description (English)", {"fields": ("footer_en", "meta_desc_en")}),
    )

    # فقط یک ردیف تنظیمات داریم: لیست را رد می‌کنیم و مستقیم می‌رویم سراغ خودِ آن
    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect(reverse("admin:core_sitesettings_change", args=[obj.pk]))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role_en", "order", "is_published")
    list_editable = ("order", "is_published")


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ("question_en", "order", "is_published")
    list_editable = ("order", "is_published")