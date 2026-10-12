from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core import views as core_views
from core.sitemaps import ProjectSitemap, StaticViewSitemap

SITEMAPS = {"pages": StaticViewSitemap, "projects": ProjectSitemap}

# این آدرس‌ها پیشوند زبان ندارند
urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", core_views.root_redirect, name="root"),
    path("robots.txt", core_views.robots, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
]

# این‌ها با /fa/ و /en/ شروع می‌شوند
urlpatterns += i18n_patterns(
    path("order/", include("orders.urls")),
    path("work/", include("portfolio.urls")),
    path("", include("core.urls")),
    prefix_default_language=True,
)

# در حالت توسعه، عکس‌های آپلودشده را خود جنگو نشان می‌دهد (روی سرور واقعی با وب‌سرور)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)