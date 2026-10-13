from django import template

from ..models import FaqItem, TeamMember

register = template.Library()


def _members(fa):
    return [
        {"m": m, "role": m.role_fa if fa else m.role_en, "initial": m.name[:1]}
        for m in TeamMember.objects.filter(is_published=True)
    ]


@register.inclusion_tag("core/about.html", takes_context=True)
def about_section(context):
    fa = context.get("lang", "fa") == "fa"
    return {"members": _members(fa), "t": context.get("t", {})}


@register.inclusion_tag("core/team.html", takes_context=True)
def team_section(context):
    fa = context.get("lang", "fa") == "fa"
    return {"members": _members(fa), "t": context.get("t", {})}


@register.inclusion_tag("core/faq.html", takes_context=True)
def faq_section(context):
    fa = context.get("lang", "fa") == "fa"
    items = [
        {
            "q": f.question_fa if fa else f.question_en,
            "a": f.answer_fa if fa else f.answer_en,
        }
        for f in FaqItem.objects.filter(is_published=True)
    ]
    return {"items": items, "t": context.get("t", {})}