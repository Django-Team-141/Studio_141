import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, URLValidator
from django.db import models

only_web_links = URLValidator(schemes=["http", "https"])

MAX_IMAGE_BYTES = 2 * 1024 * 1024
MAX_VIDEO_BYTES = 40 * 1024 * 1024


def _random_name(folder, filename):
    # اسم اصلی فایل ذخیره نمی‌شود؛ اسم تصادفی جلوی حدس زدن و تداخل را می‌گیرد
    return f"{folder}/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


def project_image_path(instance, filename):
    return _random_name("projects", filename)


def project_poster_path(instance, filename):
    return _random_name("projects/posters", filename)


def project_video_path(instance, filename):
    return _random_name("projects/videos", filename)


def validate_image_size(f):
    if f.size > MAX_IMAGE_BYTES:
        raise ValidationError("Image must be smaller than 2 MB.")


def validate_video_size(f):
    if f.size > MAX_VIDEO_BYTES:
        raise ValidationError("Video must be smaller than 40 MB. Compress it first (see the team guide).")


def validate_video_content(f):
    """نوع فایل را از محتوایش می‌خوانیم، نه از پسوندش: mp4 یا webm واقعی باشد."""
    try:
        position = f.tell()
        f.seek(0)
        head = f.read(12)
        f.seek(position)
    except (OSError, ValueError):
        return  # فایل قدیمیِ ذخیره‌شده را نمی‌شود خواند؛ جلوی ویرایش پروژه را نمی‌گیریم
    is_mp4 = head[4:8] == b"ftyp"
    is_webm = head[:4] == b"\x1a\x45\xdf\xa3"
    if not (is_mp4 or is_webm):
        raise ValidationError("This file is not a real MP4 or WebM video.")


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
    tags = models.CharField(
        max_length=120, blank=True,
        help_text="Languages and tools used, comma separated, e.g. Django, DRF, Docker. Shown as 'Built with'.",
    )
    accent = models.CharField(max_length=10, choices=ACCENTS, default="cyan")
    image = models.ImageField(
        upload_to=project_image_path,
        blank=True,
        validators=image_validators,
        help_text="Cover screenshot, jpg/png/webp, up to 2 MB. Leave empty for the colored mock.",
    )
    video = models.FileField(
        upload_to=project_video_path,
        blank=True,
        validators=[
            FileExtensionValidator(["mp4", "webm"]),
            validate_video_size,
            validate_video_content,
        ],
        help_text=(
            "Optional. mp4 (H.264) or webm, up to 40 MB, up to about 2 minutes. "
            "Run the ffmpeg 'faststart' command from the team guide before uploading."
        ),
    )
    video_poster = models.ImageField(
        upload_to=project_poster_path,
        blank=True,
        validators=image_validators,
        help_text="Optional picture shown before the video plays. jpg/png/webp, up to 2 MB.",
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

    @property
    def video_mime(self):
        return "video/webm" if self.video.name.lower().endswith(".webm") else "video/mp4"


class ProjectImage(models.Model):
    """تصویرهای بیشتر برای صفحه‌ی جزئیات پروژه."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=project_image_path, validators=image_validators)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.project.title} #{self.pk}"