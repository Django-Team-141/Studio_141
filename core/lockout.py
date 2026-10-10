import hashlib
import logging
import time

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.core.cache import cache
from django.dispatch import receiver

from .utils import client_ip

log = logging.getLogger("security")

MAX_FAILS = 5          # این‌قدر رمز اشتباه...
WINDOW = 15 * 60       # ...در این مدت (ثانیه)
BASE_LOCK = 15 * 60    # باعث قفل ۱۵ دقیقه‌ای می‌شود
MAX_LOCK = 24 * 3600   # قفل‌های بعدی دو برابر می‌شوند، تا سقف ۲۴ ساعت


def _h(value):
    # در کش و لاگ خود IP یا نام کاربری نمی‌ماند، فقط هش کوتاهش
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def _keys(request, username):
    return [
        "lock:ip:" + _h(client_ip(request)),
        "lock:user:" + _h((username or "").strip().lower()),
    ]


def is_locked(request, username):
    now = time.time()
    for key in _keys(request, username):
        state = cache.get(key)
        if state and state.get("until", 0) > now:
            return True
    return False


def record_failure(request, username):
    now = time.time()
    locked = False
    for key in _keys(request, username):
        s = cache.get(key) or {"fails": 0, "first": now, "strikes": 0, "until": 0}
        if now - s["first"] > WINDOW:
            s["fails"], s["first"] = 0, now
        s["fails"] += 1
        if s["fails"] >= MAX_FAILS:
            lock_for = min(BASE_LOCK * (2 ** s["strikes"]), MAX_LOCK)
            s.update(until=now + lock_for, strikes=s["strikes"] + 1, fails=0, first=now)
            locked = True
        cache.set(key, s, timeout=MAX_LOCK * 2)
    return locked


class LockoutBackend(ModelBackend):
    """وقتی قفل است، همان جواب «رمز اشتباه» معمولی را می‌دهد تا مهاجم چیزی نفهمد."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if request is not None and is_locked(request, username):
            # یک هش الکی می‌زنیم تا زمان پاسخ با حالت عادی فرق نکند
            get_user_model()().set_password(password or "")
            return None
        return super().authenticate(request, username=username, password=password, **kwargs)


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request=None, **kwargs):
    if request is None:
        return
    username = credentials.get("username", "")
    if is_locked(request, username):
        return
    locked = record_failure(request, username)
    log.warning(
        "login failed ip=%s user=%s%s",
        _h(client_ip(request)), _h(username.strip().lower()),
        " LOCKED" if locked else "",
    )


@receiver(user_logged_in)
def on_login_ok(sender, request=None, user=None, **kwargs):
    if request is None or user is None:
        return
    cache.delete("lock:user:" + _h(user.get_username().strip().lower()))