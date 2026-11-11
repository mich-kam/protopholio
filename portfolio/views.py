import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db import connection
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from blog.models import Post
from courses.models import Course, Order
from courses.views import owned_course_ids

from .context_processors import get_profile
from .forms import ContactForm
from .models import FAQ, GalleryPhoto, Project, Service, Skill, Testimonial, TimelineItem
from .radar import build_radar
from .security_info import SECURITY_MEASURES
from .seo import jsonld

logger = logging.getLogger(__name__)

HOME_COURSES_LIMIT = 6
LATEST_POSTS = 3
MARQUEE_CATEGORIES = {
    Skill.Category.LANGUAGES,
    Skill.Category.WEB,
    Skill.Category.DATA,
    Skill.Category.SECURITY,
}


def _sorted_skills():
    """Compétences triées selon l'ordre des catégories du modèle (requis par {% regroup %})."""
    category_rank = {value: rank for rank, value in enumerate(Skill.Category.values)}
    return sorted(
        Skill.objects.all(),
        key=lambda s: (category_rank.get(s.category, len(category_rank)), s.order, s.name),
    )


def _person_jsonld(request, profile):
    """Données structurées schema.org « Person » (aide Google à afficher une fiche claire)."""
    if not profile:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profile.full_name,
        "jobTitle": profile.headline,
        "url": request.build_absolute_uri("/"),
    }
    if profile.email:
        data["email"] = profile.email
    if profile.location:
        data["address"] = {"@type": "PostalAddress", "addressLocality": profile.location}
    if profile.photo_url:
        data["image"] = request.build_absolute_uri(profile.photo_url)
    same_as = [url for _icon, _label, url in profile.social_links]
    if same_as:
        data["sameAs"] = same_as
    return jsonld(data)


def _home_context(request, contact_form):
    profile = get_profile(request)
    skills = _sorted_skills()
    items = list(TimelineItem.objects.all())
    certifications = [i for i in items if i.kind == TimelineItem.Kind.CERTIFICATION]
    try:
        projects = list(Project.objects.prefetch_related("images").all())
    except Exception:
        # Migration pas encore appliquée : on évite une page 500.
        projects = list(Project.objects.all())
    featured_project = next((p for p in projects if p.featured), projects[0] if projects else None)
    other_projects = [p for p in projects if p != featured_project]
    try:
        gallery_photos = list(GalleryPhoto.objects.filter(is_published=True))
    except Exception:
        gallery_photos = []
    courses = list(Course.objects.published().with_ratings()[:HOME_COURSES_LIMIT])

    # Statistiques RÉELLES (jamais inventées) : un compteur à zéro est simplement masqué.
    learners = Order.objects.filter(status=Order.Status.PAID).values("user").distinct().count()
    stats = [
        (_("Projets réalisés"), len(projects)),
        (_("Certifications"), len(certifications)),
        (_("Cours en ligne"), Course.objects.published().count()),
        (_("Apprenants"), learners),
    ]

    # Pile technique affichée dans la carte de code : les 5 meilleures compétences TECHNIQUES.
    technical = [s for s in skills if s.category in MARQUEE_CATEGORIES]
    top_skills = sorted(technical, key=lambda s: -s.level)[:5]

    # Emplacements « à remplir » pour un rendu pro (visibles surtout côté admin).
    project_slots = max(0, 3 - len(projects))
    gallery_slots = max(0, 4 - len(gallery_photos))

    return {
        "skills": skills,
        "top_skills": top_skills,
        "marquee_items": [s.name for s in skills if s.category in MARQUEE_CATEGORIES],
        "security_skills": [s for s in skills if s.category == Skill.Category.SECURITY],
        "radar": build_radar(skills),
        "roles": profile.roles_list if profile else [],
        "stats": [(label, value) for label, value in stats if value > 0],
        "services": Service.objects.filter(is_published=True),
        "experiences": [i for i in items if i.kind == TimelineItem.Kind.EXPERIENCE],
        "education": [i for i in items if i.kind == TimelineItem.Kind.EDUCATION],
        "certifications": certifications,
        "projects": projects,
        "featured_project": featured_project,
        "other_projects": other_projects,
        "gallery_photos": gallery_photos,
        "project_slots": project_slots,
        "gallery_slots": gallery_slots,
        "courses": courses,
        "latest_posts": list(Post.objects.published()[:LATEST_POSTS]),
        "owned_ids": owned_course_ids(request.user),
        "testimonials": Testimonial.objects.filter(is_published=True),
        "faqs": FAQ.objects.filter(is_published=True),
        "contact_form": contact_form,
        "jsonld": _person_jsonld(request, profile),
    }


def home(request):
    """Page unique : Accueil, Services, À propos, Portfolio, Cours en ligne, FAQ et Contact."""
    return render(request, "portfolio/home.html", _home_context(request, ContactForm()))


@require_POST
def contact(request):
    # Honeypot : champ invisible que seuls les robots remplissent.
    # On feint le succès pour ne rien révéler au robot.
    if request.POST.get("website"):
        messages.success(request, _("Merci ! Votre message a bien été envoyé."))
        return redirect(f"{reverse('portfolio:home')}#contact")

    form = ContactForm(request.POST)
    if not form.is_valid():
        return render(request, "portfolio/home.html", _home_context(request, form), status=400)

    message = form.save()
    messages.success(request, _("Merci ! Votre message a bien été envoyé, je vous répondrai rapidement."))

    if settings.CONTACT_RECIPIENT:
        try:
            EmailMessage(
                subject=f"[Portfolio] {message.subject}",
                body=f"De : {message.name} <{message.email}>\n\n{message.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_RECIPIENT],
                reply_to=[message.email],
            ).send()
        except Exception:  # un e-mail raté ne doit jamais perdre le message (déjà en base)
            logger.exception("Échec d'envoi de la notification de contact.")

    return redirect(f"{reverse('portfolio:home')}#contact")


# Ordre des domaines dans le CV : la cybersécurité remonte en 2e position (visible dès la première page).
CV_CATEGORY_ORDER = [
    Skill.Category.LANGUAGES,
    Skill.Category.SECURITY,
    Skill.Category.WEB,
    Skill.Category.DATA,
    Skill.Category.SYSTEMS,
    Skill.Category.TOOLS,
]


def _cv_skills():
    rank = {value: position for position, value in enumerate(CV_CATEGORY_ORDER)}
    return sorted(
        Skill.objects.all(),
        key=lambda s: (rank.get(s.category, len(rank)), s.order, s.name),
    )


def cv(request):
    """CV en ligne, généré depuis les données du site (toujours à jour) et imprimable en PDF."""
    items = list(TimelineItem.objects.all())
    return render(
        request,
        "portfolio/cv.html",
        {
            "skills": _cv_skills(),
            "services": Service.objects.filter(is_published=True),
            "experiences": [i for i in items if i.kind == TimelineItem.Kind.EXPERIENCE],
            "education": [i for i in items if i.kind == TimelineItem.Kind.EDUCATION],
            "certifications": [i for i in items if i.kind == TimelineItem.Kind.CERTIFICATION],
            "projects": Project.objects.all(),
        },
    )


def security(request):
    """Page « Sécurité » : mesures réellement appliquées par le site + signalement de vulnérabilité."""
    return render(request, "portfolio/security.html", {"measures": SECURITY_MEASURES})


@require_GET
def security_txt(request):
    """/.well-known/security.txt (RFC 9116) : comment signaler une faille de sécurité."""
    profile = get_profile(request)
    if not profile or not profile.email:
        raise Http404
    expires = (timezone.now() + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    lines = [
        f"Contact: mailto:{profile.email}",
        f"Expires: {expires}",
        "Preferred-Languages: fr, en",
        f"Canonical: {request.build_absolute_uri('/.well-known/security.txt')}",
        # Page de politique dans la langue par défaut (security.txt n'a qu'une seule URL, hors préfixe de langue).
        f"Policy: {request.build_absolute_uri(reverse('portfolio:security'))}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


def _private_prefixes():
    """Préfixes d'URL privés dans CHAQUE langue (les segments sont traduits : /comptes/ et /en/accounts/)."""
    prefixes = []
    for code, _name in settings.LANGUAGES:
        with translation.override(code):
            accounts = reverse("accounts:login").rsplit("/", 2)[0] + "/"
            orders = reverse("courses:receipt", args=[uuid.UUID(int=0)]).rsplit("/", 3)[0] + "/"
            prefixes += [accounts, reverse("courses:dashboard"), orders]
    return prefixes


@require_GET
def robots_txt(request):
    lines = ["User-agent: *", "Disallow: /admin/"]
    lines += [f"Disallow: {prefix}" for prefix in _private_prefixes()]
    lines += ["", f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


@never_cache
@require_GET
def healthz(request):
    """Contrôle de santé pour Render/Railway/Heroku : vérifie aussi la base de données."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        logger.exception("Healthcheck : base de données injoignable.")
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})
