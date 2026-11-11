from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.home, name="home"),
    path(_("contact/"), views.contact, name="contact"),
    path(_("cv/"), views.cv, name="cv"),
    path(_("securite/"), views.security, name="security"),
]
