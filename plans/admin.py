from django.contrib import admin

from .models import Plan, PlanFeature


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 1


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("__str__", "level", "price_en", "includes_lower", "is_featured", "is_published")
    list_editable = ("includes_lower", "is_featured", "is_published")
    list_filter = ("kind", "is_published")
    inlines = [PlanFeatureInline]