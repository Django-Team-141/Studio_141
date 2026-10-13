from django.contrib import admin

from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    max_num = 6


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "accent", "has_video", "order", "is_published")
    list_editable = ("order", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectImageInline]

    fieldsets = (
        (None, {"fields": ("title", "slug", "accent", "order", "is_published")}),
        ("Text", {"fields": ("desc_fa", "desc_en", "details_fa", "details_en", "tags")}),
        ("Pictures and video", {"fields": ("image", "video", "video_poster")}),
        ("Links", {"fields": ("repo_url", "demo_url")}),
    )

    @admin.display(boolean=True, description="Video")
    def has_video(self, obj):
        return bool(obj.video)