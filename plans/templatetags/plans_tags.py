from django import template

from ..models import Plan

register = template.Library()


@register.inclusion_tag("plans/section.html", takes_context=True)
def plans_section(context):
    fa = context.get("lang", "fa") == "fa"
    groups = {"info": [], "shop": []}

    plans = Plan.objects.filter(is_published=True).prefetch_related("features")
    for p in plans:
        groups[p.kind].append({
            "p": p,
            "title": p.title_fa if fa else p.title_en,
            "price": p.price_fa if fa else p.price_en,
            "features": [f.text_fa if fa else f.text_en for f in p.features.all()],
        })

    return {
        "groups": groups,
        "has_plans": bool(groups["info"] or groups["shop"]),
        "t": context.get("t", {}),
    }