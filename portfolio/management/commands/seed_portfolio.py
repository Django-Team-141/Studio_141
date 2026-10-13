from django.core.management.base import BaseCommand

from portfolio.models import Project

# توضیح پروژه‌ی چهارم را از روی اسم مخزن و اطلاعات نسخه‌ی قبلی‌اش نوشته‌ایم.
# بعد از اجرا، از ادمین (Projects) بخوانید و با واقعیت پروژه یکی کنید.
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
    {
        "title": "Beauty Store",
        "slug": "beauty-store",
        "accent": "green",
        "tags": "Django 6, REST API, JWT",
        "desc_fa": "بک‌اند یک فروشگاه اینترنتی زیبایی با Django. محصول‌ها، سبد خرید و کاربرها را مدیریت می‌کند و ورود از راه JWT است.",
        "desc_en": "The backend of a beauty online shop, built with Django. It handles products, carts and users, with JWT login.",
        "repo_url": "https://github.com/Django-Team-141/beauty-store",
    },
]


class Command(BaseCommand):
    help = (
        "Adds the starter projects (skips the ones that already exist). "
        "Use --remove SLUG to delete a project."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--remove", action="append", default=[], metavar="SLUG",
            help="slug of a project to delete (can be repeated)",
        )

    def handle(self, *args, **options):
        for slug in options["remove"]:
            deleted, _ = Project.objects.filter(slug=slug).delete()
            self.stdout.write(("removed: " if deleted else "not found: ") + slug)

        for i, data in enumerate(STARTERS):
            _, created = Project.objects.get_or_create(
                slug=data["slug"], defaults={**data, "order": i}
            )
            self.stdout.write(("added: " if created else "exists: ") + data["title"])