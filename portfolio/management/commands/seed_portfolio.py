from django.core.management.base import BaseCommand

from portfolio.models import Project

STARTERS = [
    {
        "title": "Django Gaming Shop",
        "slug": "django-gaming-shop",
        "accent": "purple",
        "tags": "Django 5, DRF, React 19, Docker",
        "desc_fa": "فروشگاه لوازم گیمینگ با پرداخت امن، کوپن، قفل موجودی و پنل فروشنده.",
        "desc_en": "Gaming-gear store with secure checkout, coupons, stock locking and a seller panel.",
        "repo_url": "https://github.com/Django-Team-141/Django-gaming-shop",
    },
    {
        "title": "LavaGame Store",
        "slug": "lavagame-store",
        "accent": "orange",
        "tags": "Django, DRF, React/Vite, Chat",
        "desc_fa": "فروشگاه گیمینگ با سبد خرید، سفارش‌ها، پرداخت و چت پشتیبانی.",
        "desc_en": "Gaming store with cart, orders, payments and customer chat.",
        "repo_url": "https://github.com/Django-Team-141/Lavagame_store",
    },
    {
        "title": "CarZone",
        "slug": "carzone",
        "accent": "cyan",
        "tags": "Django, Frontend, Catalog",
        "desc_fa": "فروشگاه لوازم جانبی خودرو با کاتالوگ و صفحه‌ی جزئیات محصول.",
        "desc_en": "Car accessories shop with a catalog and product pages.",
        "repo_url": "https://github.com/Django-Team-141/carzone_OnlineShop",
    },
]


class Command(BaseCommand):
    help = "Adds the three starter projects (skips the ones that already exist)."

    def handle(self, *args, **options):
        for i, data in enumerate(STARTERS):
            _, created = Project.objects.get_or_create(
                slug=data["slug"], defaults={**data, "order": i}
            )
            self.stdout.write(("added: " if created else "exists: ") + data["title"])