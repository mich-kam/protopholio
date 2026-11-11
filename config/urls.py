"""
Routage principal du projet.

Langues : le français (langue par défaut) reste à la racine (/cours/), l'anglais est servi sous /en/
(/en/courses/). Les segments d'URL sont traduits (voir locale/en/LC_MESSAGES/django.po).
Restent hors du système de langues : l'administration, le sitemap, robots.txt, security.txt, le
contrôle de santé et les médias (ils doivent avoir une URL unique et stable).
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.utils.translation import gettext_lazy as _
from django.views.static import serve

from portfolio.sitemaps import sitemaps

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", include("portfolio.urls_root")),
    # Médias PUBLICS uniquement (photo de profil, captures de projets, images de cours).
    # Les fichiers de cours (courses/files/) ne sont volontairement PAS exposés ici :
    # ils ne sont téléchargeables que via la vue protégée `courses:download`.
    re_path(
        r"^media/(?P<path>(?:profile|projects|gallery|blog|courses/images)/.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]

urlpatterns += i18n_patterns(
    path(_("comptes/"), include("accounts.urls")),
    path("", include("courses.urls")),
    path("", include("blog.urls")),
    path("", include("portfolio.urls")),
    prefix_default_language=False,
)
