import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.urls import reverse, translate_url
from django.utils import translation

from .i18n import TEXTS, current_lang
from .models import SiteSettings

# فقط نام کاربری و شماره‌ی معتبر وارد لینک می‌شود
USERNAME = re.compile(r"^[A-Za-z0-9_.]{2,64}$")
NUMBER = re.compile(r"^\d{8,15}$")

# کلید متن در i18n.py ← نام فیلد در SiteSettings (با پسوند _fa یا _en)
OVERRIDES = {
    "h1_a": "hero_a",
    "h1_b": "hero_b",
    "sub": "hero_sub",
    "footer": "footer",
    "meta_desc": "meta_desc",
}


def _pick(site, field, fallback):
    """اگر در ادمین مقدار داده شده همان را می‌گیرد، وگرنه مقدار .env را."""
    value = getattr(site, field, "") if site else ""
    return (value or fallback or "").strip()


def _valid_email(value):
    try:
        validate_email(value)
    except ValidationError:
        return False
    return True


def _email(site):
    value = _pick(site, "email", settings.CONTACT_EMAIL)
    return value if value and _valid_email(value) else ""


def _contacts(t, site):
    """
    فهرست راه‌های تماس. تلگرام و ایمیل فقط وقتی هستند که تنظیم شده باشند.
    واتساپ و اینستاگرام همیشه هستند؛ تا وقتی «روشن» نشده‌اند، کارتشان «به‌زودی» است.
    """
    items = []

    tg = _pick(site, "telegram", settings.CONTACT_TELEGRAM).lstrip("@")
    if USERNAME.match(tg):
        items.append({
            "key": "telegram", "label": t["c_telegram"], "hint": t["ct_telegram_hint"],
            "live": True, "url": "https://t.me/" + tg, "display": "@" + tg, "msg": "",
        })

    email = _email(site)
    if email:
        items.append({
            "key": "email", "label": t["c_email"], "hint": t["ct_email_hint"],
            "live": True, "url": "mailto:" + email, "display": email, "msg": "",
        })

    wa = _pick(site, "whatsapp", settings.CONTACT_WHATSAPP).lstrip("+")
    wa_live = bool(site and site.whatsapp_live) and bool(NUMBER.match(wa))
    items.append({
        "key": "whatsapp", "label": t["c_whatsapp"], "hint": t["ct_whatsapp_hint"],
        "live": wa_live,
        "url": ("https://wa.me/" + wa) if wa_live else "",
        "display": ("+" + wa) if wa_live else "",
        "msg": t["soon_whatsapp"],
    })

    ig = _pick(site, "instagram", settings.CONTACT_INSTAGRAM).lstrip("@")
    ig_live = bool(site and site.instagram_live) and bool(USERNAME.match(ig))
    items.append({
        "key": "instagram", "label": t["c_instagram"], "hint": t["ct_instagram_hint"],
        "live": ig_live,
        "url": ("https://instagram.com/" + ig) if ig_live else "",
        "display": ("@" + ig) if ig_live else "",
        "msg": t["soon_instagram"],
    })

    return items


def site_language(request):
    # صفحه‌های ادمین به این اطلاعات نیازی ندارند
    if request.path.startswith("/" + settings.ADMIN_URL):
        return {}

    lang = current_lang(request)
    other = "en" if lang == "fa" else "fa"
    site = SiteSettings.objects.first()

    t = dict(TEXTS[lang])
    if site:
        for key, field in OVERRIDES.items():
            value = getattr(site, f"{field}_{lang}", "")
            if value:
                t[key] = value

    if request.method == "GET":
        other_url = translate_url(request.path, other)
        alternates = {
            code: request.build_absolute_uri(translate_url(request.path, code))
            for code in TEXTS
        }
    else:
        # بعد از یک POST (مثلاً خطای فرم) آدرس فعلی در GET معنی ندارد؛ به صفحه‌ی اصلی می‌رویم
        with translation.override(other):
            other_url = reverse("home")
        alternates = {}

    return {
        "lang": lang,
        "dir": "rtl" if lang == "fa" else "ltr",
        "t": t,
        "other_lang": other,
        "other_lang_url": other_url,
        "alternates": alternates,
        "canonical": alternates.get(lang, ""),
        "root_url": request.build_absolute_uri("/"),
        "contact": _contacts(t, site),
        "site_email": _email(site),
    }