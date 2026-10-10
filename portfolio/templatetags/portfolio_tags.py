from django import template

from ..models import Project

register = template.Library()


@register.inclusion_tag("portfolio/section.html", takes_context=True)
def portfolio_section(context):
    lang = context.get("lang", "fa")
    items = []
    for p in Project.objects.filter(is_published=True):
        items.append({
            "p": p,
            "desc": p.desc_fa if lang == "fa" else p.desc_en,
            "tags": p.tag_list(),
        })
    return {"items": items, "t": context.get("t", {})}