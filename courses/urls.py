from django.urls import path
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "courses"

# Segments traduits : /cours/<slug>/acheter/  <->  /en/courses/<slug>/buy/
urlpatterns = [
    path(_("cours/"), views.course_list, name="list"),
    path(format_lazy("{}<slug:slug>/", _("cours/")), views.course_detail, name="detail"),
    path(format_lazy("{}<slug:slug>/{}", _("cours/"), _("acheter/")), views.checkout, name="checkout"),
    path(format_lazy("{}<slug:slug>/{}", _("cours/"), _("acces/")), views.course_access, name="access"),
    path(format_lazy("{}<slug:slug>/{}", _("cours/"), _("telecharger/")), views.course_download, name="download"),
    path(format_lazy("{}<slug:slug>/{}", _("cours/"), _("avis/")), views.review_submit, name="review"),
    path(format_lazy("{}<uuid:reference>/{}", _("commande/"), _("recu/")), views.receipt, name="receipt"),
    path(_("mon-espace/"), views.dashboard, name="dashboard"),
]
