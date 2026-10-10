from django.core.management.base import BaseCommand

from plans.models import Plan, PlanFeature

# قیمت‌ها عمداً «X» است؛ عدد واقعی را خودتان از پنل ادمین بگذارید.
DATA = [
    ("info", 1, "پایه", "Basic", False, [
        ("صفحات معرفی", "Intro pages"),
        ("فرم تماس", "Contact form"),
        ("سازگار با موبایل", "Mobile friendly"),
        ("سئوی پایه", "Basic SEO"),
    ]),
    ("info", 2, "هوشمند", "Smart", True, [
        ("پنل مدیریت محتوا", "Content admin panel"),
        ("وبلاگ", "Blog"),
        ("دو زبانه", "Two languages"),
        ("چت‌بات و پیشنهاد هوشمند", "AI chatbot and suggestions"),
    ]),
    ("info", 3, "اختصاصی (سازمانی)", "Custom (Enterprise)", False, [
        ("طراحی و معماری سفارشی", "Bespoke design and architecture"),
        ("API و اتصال به سیستم‌ها", "API and integrations"),
        ("سطح‌های دسترسی", "Role-based access"),
        ("پشتیبانی اختصاصی", "Dedicated support"),
    ]),
    ("shop", 1, "پایه", "Basic", False, [
        ("کاتالوگ محصول", "Product catalog"),
        ("سبد خرید", "Cart"),
        ("پرداخت ساده", "Simple checkout"),
        ("پنل سفارش‌ها", "Order panel"),
    ]),
    ("shop", 2, "هوشمند", "Smart", True, [
        ("کوپن و تخفیف", "Coupons and discounts"),
        ("پنل فروشنده", "Seller panel"),
        ("چت پشتیبانی", "Support chat"),
        ("گزارش فروش", "Sales reports"),
    ]),
    ("shop", 3, "اختصاصی (سازمانی)", "Custom (Enterprise)", False, [
        ("چندفروشنده", "Multi-vendor"),
        ("مدیریت پیشرفته‌ی موجودی", "Advanced inventory"),
        ("اتصال به سیستم‌های داخلی", "Links to internal systems"),
        ("طراحی کاملاً سفارشی", "Fully custom design"),
    ]),
]


class Command(BaseCommand):
    help = "Adds the six starter plans with placeholder prices (skips ones that exist)."

    def handle(self, *args, **options):
        for kind, level, t_fa, t_en, hot, feats in DATA:
            plan, created = Plan.objects.get_or_create(
                kind=kind,
                level=level,
                defaults={
                    "title_fa": t_fa,
                    "title_en": t_en,
                    "price_fa": "از X تومان",
                    "price_en": "from X",
                    "is_featured": hot,
                },
            )
            if created:
                for i, (fa, en) in enumerate(feats):
                    PlanFeature.objects.create(plan=plan, text_fa=fa, text_en=en, order=i)
            self.stdout.write(("added: " if created else "exists: ") + str(plan))