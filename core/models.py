import uuid
from pathlib import Path

from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models

from portfolio.models import only_web_links, validate_image_size

username_ok = RegexValidator(
    r"^@?[A-Za-z0-9_.]{2,64}$",
    "Only the username, like my_studio (not a link).",
)
number_ok = RegexValidator(
    r"^\+?\d{8,15}$",
    "Digits with the country code, like 989121234567.",
)

EMPTY_HINT = "Leave empty to use the default."


class SiteSettings(models.Model):
    """تنظیمات سایت. فقط یک ردیف دارد و از پنل ادمین ویرایش می‌شود."""

    # --- راه‌های تماس ---
    telegram = models.CharField(
        max_length=65, blank=True, validators=[username_ok],
        help_text="Username only. Empty = use CONTACT_TELEGRAM from the server settings.",
    )
    email = models.EmailField(
        blank=True,
        help_text="The team email. Shown in the contact section and the footer. Empty = use CONTACT_EMAIL from the server settings.",
    )
    whatsapp = models.CharField(
        max_length=16, blank=True, validators=[number_ok],
        help_text="Number with country code. Empty = use CONTACT_WHATSAPP from the server settings.",
    )
    whatsapp_live = models.BooleanField(
        "WhatsApp is live", default=False,
        help_text="Tick this when the WhatsApp number works. Until then visitors see 'coming soon'.",
    )
    instagram = models.CharField(
        max_length=65, blank=True, validators=[username_ok],
        help_text="Username only. Empty = use CONTACT_INSTAGRAM from the server settings.",
    )
    instagram_live = models.BooleanField(
        "Instagram is live", default=False,
        help_text="Tick this when the Instagram page is ready. Until then visitors see 'coming soon'.",
    )

    # --- متن هدر ---
    hero_a_fa = models.CharField("Hero first line (Persian)", max_length=80, blank=True, help_text=EMPTY_HINT)
    hero_a_en = models.CharField("Hero first line (English)", max_length=80, blank=True, help_text=EMPTY_HINT)
    hero_b_fa = models.CharField("Hero glowing words (Persian)", max_length=80, blank=True, help_text=EMPTY_HINT)
    hero_b_en = models.CharField("Hero glowing words (English)", max_length=80, blank=True, help_text=EMPTY_HINT)
    hero_sub_fa = models.TextField("Hero sentence (Persian)", max_length=300, blank=True, help_text=EMPTY_HINT)
    hero_sub_en = models.TextField("Hero sentence (English)", max_length=300, blank=True, help_text=EMPTY_HINT)

    # --- فوتر و توضیح سئو ---
    footer_fa = models.CharField("Footer text (Persian)", max_length=120, blank=True, help_text=EMPTY_HINT)
    footer_en = models.CharField("Footer text (English)", max_length=120, blank=True, help_text=EMPTY_HINT)
    meta_desc_fa = models.CharField(
        "Search description (Persian)", max_length=200, blank=True,
        help_text="The grey text under the title in Google. About 150 characters. " + EMPTY_HINT,
    )
    meta_desc_en = models.CharField(
        "Search description (English)", max_length=200, blank=True,
        help_text="The grey text under the title in Google. About 150 characters. " + EMPTY_HINT,
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # همیشه همان یک ردیف
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


def team_photo_path(instance, filename):
    # اسم تصادفی، تا اسم اصلی فایل ذخیره نشود
    ext = Path(filename).suffix.lower()
    return f"team/{uuid.uuid4().hex}{ext}"


class TeamMember(models.Model):
    name = models.CharField(max_length=60)
    role_fa = models.CharField("Role (Persian)", max_length=80)
    role_en = models.CharField("Role (English)", max_length=80)
    photo = models.ImageField(
        upload_to=team_photo_path,
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_image_size],
        help_text="Optional, square works best, jpg/png/webp up to 2 MB. Empty = the first letter of the name.",
    )
    link = models.URLField(blank=True, validators=[only_web_links], help_text="Optional: GitHub or LinkedIn page.")
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class FaqItem(models.Model):
    question_fa = models.CharField(max_length=200)
    question_en = models.CharField(max_length=200)
    answer_fa = models.TextField(max_length=600)
    answer_en = models.TextField(max_length=600)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.question_en