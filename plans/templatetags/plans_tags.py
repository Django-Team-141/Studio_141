from django import template

from ..models import Plan

register = template.Library()


def _rows(cards):
    """ماتریس مقایسه: هر ویژگی یک ردیف، هر پلن یک ستون."""
    rows = []
    for i, card in enumerate(cards):
        for text in card["features"]:
            cells = []
            for j in range(len(cards)):
                if j < i:
                    cells.append(False)
                elif j == i:
                    cells.append(True)
                else:
                    # پلن بالاتر فقط وقتی این ویژگی را دارد که همه‌ی پلن‌های بین i تا j «شامل پایین‌تر» باشند
                    cells.append(all(cards[k]["p"].includes_lower for k in range(i + 1, j + 1)))
            rows.append({"text": text, "cells": cells})
    return rows


@register.inclusion_tag("plans/section.html", takes_context=True)
def plans_section(context):
    fa = context.get("lang", "fa") == "fa"
    groups = {"info": {"cards": []}, "shop": {"cards": []}}

    plans = Plan.objects.filter(is_published=True).prefetch_related("features")
    for p in plans:
        groups[p.kind]["cards"].append({
            "p": p,
            "title": p.title_fa if fa else p.title_en,
            "price": p.price_fa if fa else p.price_en,
            "features": [f.text_fa if fa else f.text_en for f in p.features.all()],
        })

    for g in groups.values():
        cards = g["cards"]
        g["rows"] = _rows(cards) if len(cards) >= 2 else []
        g["cumulative"] = any(c["p"].includes_lower for c in cards[1:])

    return {
        "groups": groups,
        "has_plans": bool(groups["info"]["cards"] or groups["shop"]["cards"]),
        "t": context.get("t", {}),
    }