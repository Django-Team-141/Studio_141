import json
import logging
import threading
import urllib.request

from django.conf import settings

log = logging.getLogger("orders")


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


def build_text(order):
    plan = str(order.plan) if order.plan else "-"
    lines = [
        "🔔 درخواست جدید",
        f"کد: {order.code}",
        f"پلن: {plan}",
        f"زبان مشتری: {order.lang}",
    ]
    if settings.TELEGRAM_FULL_DETAILS:
        lines.append(f"نام: {order.name}")
        lines.append(f"شماره: {order.phone}")
        if order.email:
            lines.append(f"ایمیل: {order.email}")
        if order.message:
            lines.append("توضیح: " + order.message[:300])
    else:
        lines.append(f"شماره: {order.masked_phone()}")
        lines.append("جزئیات کامل را در پنل ادمین ببینید.")
    return "\n".join(lines)


def _send(text):
    try:
        api("sendMessage", {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": text,
            "disable_web_page_preview": True,
        })
    except Exception as exc:
        # فقط نوع خطا را لاگ می‌کنیم؛ متن خطا ممکن است آدرسِ دارای توکن را داشته باشد
        log.warning("telegram notify failed: %s", type(exc).__name__)


def notify_new_order(order):
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return
    # در یک نخ جدا می‌فرستیم تا اگر تلگرام کند یا قطع بود، مشتری منتظر نماند
    threading.Thread(target=_send, args=(build_text(order),), daemon=True).start()