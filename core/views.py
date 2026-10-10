from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .i18n import TEXTS


def home(request):
    return render(request, "core/home.html")


def privacy(request):
    return render(request, "core/privacy.html")


def set_language(request, code):
    if code in TEXTS:
        request.session["lang"] = code
    back = request.META.get("HTTP_REFERER", "/")
    if not url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}):
        back = "/"
    return redirect(back)