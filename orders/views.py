import hashlib

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from core.i18n import current_lang
from core.utils import client_ip

from .forms import OrderForm
from .models import make_code
from .throttle import allow


def _hash(value):
    # خود IP یا شماره را در کش نگه نمی‌داریم، فقط هش آن را
    return hashlib.sha256(value.encode()).hexdigest()[:24]


@require_http_methods(["GET", "POST"])
def submit(request):
    # اگر کسی بعد از یک خطا صفحه را رفرش کرد یا آدرس را مستقیم باز کرد، به خود فرم برمی‌گردد
    if request.method == "GET":
        return redirect(reverse("home") + "#order")

    lang = current_lang(request)
    ip = client_ip(request)

    if not allow("ord-ip:" + _hash(ip), limit=10, window=3600):
        return render(request, "orders/page.html", {"throttled": True}, status=429)

    form = OrderForm(request.POST, lang=lang)
    if not form.is_valid():
        return render(request, "orders/page.html", {"form": form}, status=400)

    # ربات‌ها فکر می‌کنند ثبت شده، ولی چیزی ذخیره نمی‌شود
    if form.cleaned_data.get("website"):
        request.session["last_order"] = make_code()
        return redirect("orders:done")

    if not allow("ord-phone:" + _hash(form.cleaned_data["phone"]), limit=3, window=86400):
        return render(request, "orders/page.html", {"throttled": True}, status=429)

    order = form.save(commit=False)
    order.lang = lang
    order.save()

    request.session["last_order"] = order.code
    return redirect("orders:done")


@require_GET
def done(request):
    code = request.session.get("last_order")
    if not code:
        return redirect(reverse("home") + "#order")
    return render(request, "orders/done.html", {"code": code})