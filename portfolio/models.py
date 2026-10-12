import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, URLValidator
from django.db import models

only_web_links = URLValidator(schemes=["http", "https"])


def project_image_path(instance, filename):
    # اسم اصلی فایل ذخیره نمی‌شود؛ اسم تصادفی جلوی حدس زدن و تداخل را می‌گیرد
    ext = Path(filename).suffix.lower()
    return f"projects/{uuid.uuid4().hex}{ext}"


def validate_image_size(f):
    if f.size > 2 * 1024 * 1024:
        raise ValidationError("Image must be smaller than 2 MB.")


image_validators = [
    FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
    validate_image_size,
]


class Project(models.Model):
    ACCENTS = [
        ("cyan", "Cyan"),
        ("green", "Green"),
        ("purple", "Purple"),
        ("orange", "Orange"),
        ("pink", "Pink"),
    ]

    title = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    desc_fa = models.TextField("Description (Persian)", max_length=300)
    desc_en = models.TextField("Description (English)", max_length=300)
    details_fa = models.TextField(
        "Details page text (Persian)", max_length=2000, blank=True,
        help_text="Optional. Shown on the project's own page. A blank line starts a new paragraph.",
    )
    details_en = models.TextField(
        "Details page text (English)", max_length=2000, blank=True,
        help_text="Optional. Shown on the project's own page. A blank line starts a new paragraph.",
    )
    tags = models.CharField(max_length=120, blank=True, help_text="Comma separated, e.g. Django, DRF, Docker")
    accent = models.CharField(max_length=10, choices=ACCENTS, default="cyan")
    image = models.ImageField(
        upload_to=project_image_path,
        blank=True,
        validators=image_validators,
        help_text="Cover screenshot, jpg/png/webp, up to 2 MB. Leave empty for the colored mock.",
    )
    repo_url = models.URLField(blank=True, validators=[only_web_links])
    demo_url = models.URLField(blank=True, validators=[only_web_links])
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def tag_list(self):
        return [x.strip() for x in self.tags.split(",") if x.strip()]


class ProjectImage(models.Model):
    """تصویرهای بیشتر برای صفحه‌ی جزئیات پروژه."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=project_image_path, validators=image_validators)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.project.title} #{self.pk}"