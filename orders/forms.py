import re

from django import forms
from django.core.exceptions import ValidationError

from plans.models import Plan

from .models import Order

# ارقام فارسی و عربی را به لاتین تبدیل می‌کنیم
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

MSG = {
    "fa": {
        "required": "این قسمت را پر کنید.",
        "phone": "این شماره درست به نظر نمی‌رسد. چیزی شبیه 09121234567 یا +989121234567 بنویسید.",
        "email": "ایمیل را درست وارد نکرده‌اید.",
        "max": "متنتان از حد مجاز بلندتر است.",
        "plan_bad": "این پلن را پیدا نکردیم. لطفاً یکی از گزینه‌های لیست را انتخاب کنید.",
        "plan_none": "هنوز نمی‌دانم 🤷",
    },
    "en": {
        "required": "Please fill this in.",
        "phone": "That phone number doesn't look right. Try something like +989121234567.",
        "email": "That email address doesn't look right.",
        "max": "That's a bit longer than we can take.",
        "plan_bad": "We couldn't find that plan. Please pick one from the list.",
        "plan_none": "Not sure yet",
    },
}

KIND = {
    "fa": {"info": "معرفی", "shop": "فروشگاهی"},
    "en": {"info": "Company/personal", "shop": "Store"},
}


class OrderForm(forms.ModelForm):
    # تله برای ربات‌ها: آدم این فیلد را نمی‌بیند و پرش نمی‌کند
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    class Meta:
        model = Order
        fields = ["name", "phone", "email", "plan", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name", "maxlength": 80}),
            "phone": forms.TextInput(attrs={"inputmode": "tel", "autocomplete": "tel", "maxlength": 20}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "message": forms.Textarea(attrs={"rows": 4, "maxlength": 1000}),
        }

    def __init__(self, *args, lang="fa", **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang if lang in MSG else "fa"
        m = MSG[self.lang]

        for field in self.fields.values():
            field.error_messages["required"] = m["required"]
            field.error_messages["max_length"] = m["max"]
        self.fields["email"].error_messages["invalid"] = m["email"]

        plan = self.fields["plan"]
        plan.queryset = Plan.objects.filter(is_published=True).order_by("kind", "level")
        plan.empty_label = m["plan_none"]
        plan.error_messages["invalid_choice"] = m["plan_bad"]
        plan.label_from_instance = self._plan_label

    def _plan_label(self, p):
        title = p.title_fa if self.lang == "fa" else p.title_en
        return f"{KIND[self.lang][p.kind]} · {title}"

    def clean_phone(self):
        raw = self.cleaned_data["phone"].translate(DIGITS)
        phone = re.sub(r"[\s\-()]", "", raw)
        if not re.fullmatch(r"\+?\d{7,15}", phone):
            raise ValidationError(MSG[self.lang]["phone"])
        return phone