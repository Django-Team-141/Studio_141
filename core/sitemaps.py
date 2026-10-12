from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from portfolio.models import Project


class StaticViewSitemap(Sitemap):
    """صفحه‌های ثابت سایت، برای هر دو زبان، با لینک hreflang بین آن‌ها."""

    i18n = True
    alternates = True
    x_default = True
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ["home", "privacy"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    """صفحه‌ی جزئیات هر نمونه‌کار منتشرشده."""

    i18n = True
    alternates = True
    x_default = True
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Project.objects.filter(is_published=True)

    def location(self, item):
        return reverse("portfolio:detail", args=[item.slug])