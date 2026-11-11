"""Routes techniques à URL unique (hors préfixe de langue) : robots.txt, security.txt, santé."""

from django.urls import path

from . import views

app_name = "root"

urlpatterns = [
    path("robots.txt", views.robots_txt, name="robots"),
    path("healthz/", views.healthz, name="healthz"),
    path(".well-known/security.txt", views.security_txt, name="security_txt"),
]
