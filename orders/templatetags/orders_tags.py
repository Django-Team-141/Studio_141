from django import template

from ..forms import OrderForm

register = template.Library()


@register.inclusion_tag("orders/section.html", takes_context=True)
def order_section(context):
    request = context["request"]
    initial = {}

    # دکمه‌ی «این پلن را می‌خواهم» آدرس ?plan=شماره می‌فرستد
    pid = request.GET.get("plan", "")
    if pid.isascii() and pid.isdigit():
        initial["plan"] = int(pid)

    return {
        "form": OrderForm(initial=initial, lang=context.get("lang", "fa")),
        "t": context.get("t", {}),
        "csrf_token": context.get("csrf_token"),
    }