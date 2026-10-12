from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation
from django.utils.cache import patch_vary_headers
from django.views.decorators.http import require_GET

from .i18n import DEFAULT_LANG, TEXTS


def home(request):
    return render(request, "core/home.html")


def privacy(request):
    return render(request, "core/privacy.html")


@require_GET
def root_redirect(request):
    """آدرس «/» را بر اساس زبان مرورگر به /fa/ یا /en/ می‌فرستد."""
    lang = translation.get_language_from_request(request)
    if lang not in TEXTS:
        lang = DEFAULT_LANG
    with translation.override(lang):
        url = reverse("home")
    response = HttpResponseRedirect(url)
    patch_vary_headers(response, ["Accept-Language"])
    return response


@require_GET
def robots(request):
    disallow = []
    for code in TEXTS:
        with translation.override(code):
            disallow.append("Disallow: " + reverse("orders:submit"))

    lines = ["User-agent: *", "Allow: /"] + disallow + [
        "",
        "Sitemap: " + request.build_absolute_uri(reverse("sitemap")),
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")