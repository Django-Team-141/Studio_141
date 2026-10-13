import json

from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def org_jsonld(context):
    """داده‌ی ساختاریافته‌ی معرفی استودیو برای گوگل (فقط صفحه‌ی اصلی)."""
    request = context["request"]
    t = context.get("t", {})

    data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": "141 · One for One",
        "description": t.get("meta_desc", ""),
        "url": request.build_absolute_uri(request.path),
        "logo": request.build_absolute_uri(static("img/apple-touch-icon.png")),
        "image": request.build_absolute_uri(static("img/og-image.png")),
        "availableLanguage": ["fa", "en"],
    }
    # فقط پروفایل‌هایی که واقعاً فعال‌اند
    same_as = [
        c["url"] for c in context.get("contact", [])
        if c.get("live") and c["key"] in ("telegram", "instagram")
    ]
    if same_as:
        data["sameAs"] = same_as
    if context.get("site_email"):
        data["email"] = context["site_email"]

    text = json.dumps(data, ensure_ascii=False)
    # این سه نویسه نباید بتوانند تگ script را ببندند
    text = text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe('<script type="application/ld+json">' + text + "</script>")