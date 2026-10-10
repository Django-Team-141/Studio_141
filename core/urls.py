from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("privacy/", views.privacy, name="privacy"),
    path("lang/<str:code>/", views.set_language, name="set_language"),
]