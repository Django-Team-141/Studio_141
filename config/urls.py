from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("order/", include("orders.urls")),
    path("", include("core.urls")),
]

# در حالت توسعه، عکس‌های آپلودشده را خود جنگو نشان می‌دهد (روی سرور واقعی در پارت ۶ با وب‌سرور)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)