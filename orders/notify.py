import html
import json
import logging
import re
import threading
import urllib.request

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

log = logging.getLogger("orders")

KIND_FA = {"info": "معرفی شخص / شرکت", "shop": "فروشگاهی"}
LANG_FA = {"fa": "فارسی", "en": "English"}

# چهار جا برای شماره‌ی چت اعضای تیم؛ داخل هرکدام هم می‌شود چند شماره با ویرگول گذاشت
CHAT_ID_SETTINGS = (
    "TELEGRAM_CHAT_ID",
    "TELEGRAM_CHAT_ID_2",
    "TELEGRAM_CHAT_ID_3",
    "TELEGRAM_CHAT_ID_4",
)
CHAT_ID = re.compile(r"^-?\d{1,20}$")


def api(method, payload=None, timeout=8):
    """یک درخواست به Bot API تلگرام. نتیجه‌ی JSON را برمی‌گرداند."""
    base = settings.TELEGRAM_API_BASE.rstrip("/")
    if not base.startswith("https://"):
        raise ValueError("TELEGRAM_API_BASE must start with https://")
    url = f"{base}/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def error_label(exc):
    """نوع خطا (و کد HTTP اگر داشت). متن خطا را نمی‌آوریم، چون ممکن است آدرسِ دارای توکن را داشته باشد."""
    code = getattr(exc, "code", None)
    return f"{type(exc).__name__} {code}" if code else type(exc).__name__


def chat_ids():
    """شماره‌ی چت همه‌ی دریافت‌کننده‌ها، بدون تکرار و به ترتیب. چیزی که عدد نباشد نادیده گرفته می‌شود."""
    found = []
    for name in CHAT_ID_SETTINGS:
        for raw in str(getattr(settings, name, "")).split(","):
            value = raw.strip()
            if not value:
                continue
            if not CHAT_ID.match(value):
                log.warning("telegram: a value in %s is not a chat number, so it is ignored", name)
                continue
            if value not in found:
                found.append(value)
    return found


def email_enabled():
    return bool(settings.EMAIL_HOST and settings.ORDER_NOTIFY_EMAIL_TO)


def _e(value):
    """متن مشتری را برای پیام HTML تلگرام امن می‌کند."""
    return html.escape(str(value), quote=False)


def _plan_line(order):
    plan = order.plan
    if not plan:
        return "انتخاب نشده"
    return f"{KIND_FA.get(plan.kind, plan.kind)} · {plan.title_fa} ({plan.price_fa})"


def _when(order):
    moment = order.created_at or timezone.now()
    return timezone.localtime(moment).strftime("%Y-%m-%d %H:%M")


def build_text(order):
    """متن پیام تلگرام. عین فرم سایت: نام، شماره، ایمیل، پلن، توضیحات، و کد پیگیری."""
    lines = [
        "🆕 <b>درخواست جدید</b>",
        f"🔖 کد پیگیری: <code>{_e(order.code)}</code>",
        "",
    ]
    if settings.TELEGRAM_FULL_DETAILS:
        lines += [
            f"👤 <b>نام:</b> {_e(order.name)}",
            f"📞 <b>شماره:</b> <code>{_e(order.phone)}</code>",
            f"✉️ <b>ایمیل:</b> {_e(order.email) if order.email else '—'}",
            f"🧩 <b>پلن:</b> {_e(_plan_line(order))}",
            "📝 <b>توضیحات:</b>",
            _e(order.message) if order.message else "—",
        ]
    else:
        lines += [
            f"📞 <b>شماره:</b> <code>{_e(order.masked_phone())}</code>",
            f"🧩 <b>پلن:</b> {_e(_plan_line(order))}",
            "جزئیات کامل را در پنل ادمین ببینید.",
        ]
    lines += ["", f"🕒 {_when(order)} · زبان مشتری: {LANG_FA.get(order.lang, order.lang)}"]
    return "\n".join(lines)


def build_email(order):
    """موضوع و متن ایمیل (متن ساده)."""
    subject = f"درخواست جدید ۱۴۱ · {order.code}"
    body = "\n".join([
        f"کد پیگیری: {order.code}",
        f"زمان ثبت: {_when(order)}",
        f"زبان مشتری: {LANG_FA.get(order.lang, order.lang)}",
        "",
        f"نام: {order.name}",
        f"شماره: {order.phone}",
        f"ایمیل: {order.email or '—'}",
        f"پلن: {_plan_line(order)}",
        "",
        "توضیحات:",
        order.message or "—",
        "",
        "این کد همان کدی است که بعد از ثبت درخواست به مشتری نشان داده شد.",
    ])
    return subject, body


def _send_telegram(text):
    for number, chat_id in enumerate(chat_ids(), start=1):
        try:
            api("sendMessage", {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            })
        except Exception as exc:
            # شماره‌ی چت را در لاگ نمی‌گذاریم، فقط ترتیبش را
            log.warning("telegram notify failed for chat %s: %s", number, error_label(exc))


def _send_email(subject, body, reply_to):
    try:
        EmailMessage(
            subject, body,
            to=list(settings.ORDER_NOTIFY_EMAIL_TO),
            reply_to=[reply_to] if reply_to else None,
        ).send()
    except Exception as exc:
        log.warning("email notify failed: %s", error_label(exc))


def notify_new_order(order):
    # متن‌ها را همین‌جا می‌سازیم (نه داخل نخ)، چون خواندن پلن از دیتابیس است
    # و هر نخ جدا اتصال دیتابیس جدا باز می‌کند.
    # هر کانال در نخ جدا می‌فرستد تا اگر کند بود، مشتری منتظر نماند.
    if settings.TELEGRAM_BOT_TOKEN and chat_ids():
        threading.Thread(target=_send_telegram, args=(build_text(order),), daemon=True).start()

    if email_enabled():
        subject, body = build_email(order)
        threading.Thread(
            target=_send_email, args=(subject, body, order.email), daemon=True
        ).start()