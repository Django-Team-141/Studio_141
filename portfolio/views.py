from django.http import Http404
from django.shortcuts import get_object_or_404, render

from core.i18n import current_lang

from .models import Project


def detail(request, slug):
    p = get_object_or_404(Project.objects.prefetch_related("images"), slug=slug, is_published=True)
    fa = current_lang(request) == "fa"
    return render(request, "portfolio/detail.html", {
        "p": p,
        "desc": p.desc_fa if fa else p.desc_en,
        "details": p.details_fa if fa else p.details_en,
        "tags": p.tag_list(),
        "images": list(p.images.all()),
    })


def video(request, slug):
    p = get_object_or_404(Project, slug=slug, is_published=True)
    if not p.video:
        raise Http404("This project has no video.")
    fa = current_lang(request) == "fa"
    return render(request, "portfolio/video.html", {
        "p": p,
        "desc": p.desc_fa if fa else p.desc_en,
    })