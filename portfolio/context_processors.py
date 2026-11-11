from django.conf import settings
from django.templatetags.static import static

from .models import GalleryPhoto, Profile, Skill, _static_exists

SOCIAL_CARD = "img/social-card.jpg"


def get_profile(request):
    """Profil du site, lu une seule fois par requête (partagé entre vue et templates)."""
    if not hasattr(request, "_site_profile"):
        request._site_profile = Profile.objects.first()
    return request._site_profile


def _og_image(request, profile):
    """Image d'aperçu pour les partages : carte sociale générée, sinon photo de profil."""
    if _static_exists(SOCIAL_CARD):
        return request.build_absolute_uri(static(SOCIAL_CARD))
    if profile and profile.photo_url:
        return request.build_absolute_uri(profile.photo_url)
    return ""


def site_context(request):
    """Variables disponibles dans TOUS les templates (navbar, footer, SEO, prix...)."""
    profile = get_profile(request)
    try:
        has_gallery = GalleryPhoto.objects.filter(is_published=True).exists()
    except Exception:
        has_gallery = False
    staff = getattr(request.user, "is_staff", False)
    return {
        "profile": profile,
        "CURRENCY_SYMBOL": settings.CURRENCY_SYMBOL,
        # SEO : URL canonique (sans paramètres de requête) et image de partage.
        "canonical_url": request.build_absolute_uri(request.path),
        "site_url": request.build_absolute_uri("/"),
        "og_image": _og_image(request, profile),
        "nav_show_security": Skill.objects.filter(category=Skill.Category.SECURITY).exists(),
        "nav_show_gallery": has_gallery or staff,
    }
