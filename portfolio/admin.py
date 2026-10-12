from django.contrib import admin

from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    max_num = 6


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "accent", "order", "is_published")
    list_editable = ("order", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectImageInline]