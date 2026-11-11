"""
Configuration Django du projet.

Toute la configuration sensible ou dépendante de l'environnement est lue
depuis les variables d'environnement (os.environ). En local, elles sont
chargées depuis un fichier `.env` (voir `.env.example`).
"""

import os
import sys
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Charge .env en local. En production (Render, Railway, Heroku) les variables
# sont fournies directement par la plateforme : le fichier n'existe pas.
load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# --------------------------------------------------------------------------
# Sécurité de base
# --------------------------------------------------------------------------
# DEBUG vaut False par défaut : on n'active jamais le mode debug « par oubli ».
DEBUG = env_bool("DEBUG", False)
TESTING = "test" in sys.argv

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG or TESTING:
        SECRET_KEY = "django-insecure-cle-de-developpement-uniquement"
    else:
        raise ImproperlyConfigured(
            "La variable d'environnement SECRET_KEY est obligatoire quand DEBUG=False."
        )

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]" if DEBUG else "")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# Les plateformes exposent automatiquement leur nom de domaine public.
for _host_var in ("RENDER_EXTERNAL_HOSTNAME", "RAILWAY_PUBLIC_DOMAIN"):
    _host = os.environ.get(_host_var)
    if _host:
        ALLOWED_HOSTS.append(_host)
        CSRF_TRUSTED_ORIGINS.append(f"https://{_host}")


# --------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    # Doit précéder django.contrib.admin : ajoute les champs « français / anglais » dans l'administration.
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # Applications du projet
    "accounts",
    "portfolio",
    "courses",
    "blog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Détermine la langue d'après le préfixe de l'URL (/en/...). Après la session, avant CommonMiddleware.
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.PermissionsPolicyMiddleware",
]

if not (DEBUG or TESTING):
    # WhiteNoise sert les fichiers statiques directement depuis gunicorn (production).
    # Doit se placer juste après SecurityMiddleware. En développement, `runserver`
    # s'en charge déjà via django.contrib.staticfiles.
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",  # LANGUAGE_CODE, LANGUAGES dans les templates
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "portfolio.context_processors.site_context",
            ],
            # Balises disponibles partout sans `{% load %}` : {% icon "check" %}, {% trans "..." %}...
            "builtins": ["django.templatetags.i18n", "portfolio.templatetags.ui"],
        },
    },
]


# --------------------------------------------------------------------------
# Base de données
# --------------------------------------------------------------------------
# SQLite en local ; PostgreSQL dès que DATABASE_URL est défini
# (Render, Railway et Heroku le fournissent avec leur add-on PostgreSQL).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
if os.environ.get("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=env_bool("DATABASE_SSL_REQUIRE", False),
    )


# --------------------------------------------------------------------------
# Authentification
# --------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

# Connexion possible avec le nom d'utilisateur OU l'adresse e-mail.
AUTHENTICATION_BACKENDS = ["accounts.backends.EmailOrUsernameBackend"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "courses:dashboard"
LOGOUT_REDIRECT_URL = "portfolio:home"


# --------------------------------------------------------------------------
# Internationalisation
# --------------------------------------------------------------------------
LANGUAGE_CODE = "fr"  # langue par défaut (URLs sans préfixe) ; l'anglais est servi sous /en/
LANGUAGES = [("fr", "Français"), ("en", "English")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Africa/Kinshasa"
USE_I18N = True
USE_TZ = True

# Contenu stocké en base (profil, cours, articles...) : une colonne par langue (django-modeltranslation).
# Si une traduction anglaise est vide, le texte français est affiché à la place.
MODELTRANSLATION_DEFAULT_LANGUAGE = "fr"
MODELTRANSLATION_LANGUAGES = ("fr", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("fr",)


# --------------------------------------------------------------------------
# Fichiers statiques (WhiteNoise) et médias
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# En production : compression + noms de fichiers hachés (cache longue durée).
# En développement/tests : stockage simple (pas besoin de lancer collectstatic).
_static_backend = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
    if (DEBUG or TESTING)
    else "whitenoise.storage.CompressedManifestStaticFilesStorage"
)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": _static_backend},
}

MEDIA_URL = "/media/"
# ATTENTION : le disque de Render/Heroku est éphémère. Pour des médias durables,
# utilisez un disque persistant (MEDIA_ROOT) ou un stockage objet (S3, Cloudinary).
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------------------------------------
# Durcissement en production
# --------------------------------------------------------------------------
if not (DEBUG or TESTING):
    # Les plateformes terminent le TLS en amont et transmettent ce header.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    # Le contrôle de santé de la plateforme passe en HTTP interne : pas de redirection.
    SECURE_REDIRECT_EXEMPT = [r"^healthz/$"]
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 60 * 60 * 24 * 365))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"


# --------------------------------------------------------------------------
# E-mail (notifications du formulaire de contact)
# --------------------------------------------------------------------------
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
else:
    # Sans serveur SMTP configuré, les e-mails sont simplement écrits dans les logs.
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@localhost")

# Adresse qui reçoit les messages du formulaire de contact (optionnel).
CONTACT_RECIPIENT = os.environ.get("CONTACT_RECIPIENT", "")


# --------------------------------------------------------------------------
# Paramètres métier
# --------------------------------------------------------------------------
CURRENCY_SYMBOL = os.environ.get("CURRENCY_SYMBOL", "$")
CURRENCY_CODE = os.environ.get("CURRENCY_CODE", "USD")  # code ISO 4217 (données structurées SEO)

# Flutterwave : carte + Mobile Money. Sans clé secrète = paiement simulé (démo).
FLUTTERWAVE_PUBLIC_KEY = os.environ.get("FLUTTERWAVE_PUBLIC_KEY", "")
FLUTTERWAVE_SECRET_KEY = os.environ.get("FLUTTERWAVE_SECRET_KEY", "")


# --------------------------------------------------------------------------
# Logs : tout sur la sortie standard (collectée par Render/Railway/Heroku)
# --------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
}
