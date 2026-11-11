from functools import lru_cache

from django.contrib.staticfiles import finders
from django.core.validators import MaxValueValidator
from django.db import models
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

# Photo livrée avec le site : elle survit aux redéploiements (le disque des médias, lui, est éphémère).
DEFAULT_PHOTO = "img/profile.jpg"


@lru_cache(maxsize=None)
def _static_exists(path):
    return finders.find(path) is not None


class Profile(models.Model):
    """
    Informations personnelles affichées sur le site (page « À propos », hero, contact).
    Conçu pour n'avoir qu'UNE seule fiche : l'admin interdit d'en créer une seconde.
    """

    full_name = models.CharField("nom complet", max_length=120)
    headline = models.CharField(
        "titre professionnel", max_length=160, help_text="Ex. : Développeur Python / Django"
    )
    roles = models.CharField(
        "rôles animés",
        max_length=255,
        blank=True,
        help_text="Affichés en alternance (effet machine à écrire) en page d'accueil, séparés par des "
        "virgules. Ex. : Développeur web, Spécialiste cybersécurité, Formateur",
    )
    tagline = models.CharField(
        "accroche", max_length=255, blank=True, help_text="Phrase courte affichée en page d'accueil."
    )
    about = models.TextField("à propos / parcours", blank=True)
    photo = models.ImageField(
        "photo de profil",
        upload_to="profile/",
        blank=True,
        help_text="Portrait professionnel (recommandé : 800×1000 px, visage bien visible). "
        "Sans photo, static/img/profile.jpg est utilisé. Affichée dans le hero et la section À propos.",
    )
    cv_file = models.FileField(
        "CV (PDF)",
        upload_to="profile/cv/",
        blank=True,
        help_text="Fichier PUBLIC : retirez-en les données sensibles (passeport, adresse exacte...).",
    )

    email = models.EmailField("e-mail", blank=True)
    phone = models.CharField("téléphone", max_length=40, blank=True)
    location = models.CharField("localisation", max_length=120, blank=True)
    languages = models.CharField(
        "langues", max_length=255, blank=True, help_text="Ex. : Français (C2) · Anglais (B2)"
    )

    whatsapp = models.CharField(
        "WhatsApp",
        max_length=40,
        blank=True,
        help_text="Numéro international, ex. : +243810081623. Affiche un bouton WhatsApp sur le site.",
    )
    github_url = models.URLField("GitHub", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    facebook_url = models.URLField("Facebook", blank=True)
    youtube_url = models.URLField("YouTube", blank=True)

    available_for_work = models.BooleanField(
        "disponible pour de nouvelles missions",
        default=True,
        help_text="Affiche un badge « Disponible » en page d'accueil.",
    )

    class Meta:
        verbose_name = "profil"
        verbose_name_plural = "profil"

    def __str__(self):
        return self.full_name

    @property
    def initials(self):
        parts = [p for p in self.full_name.split() if p]
        return "".join(p[0] for p in parts[:2]).upper() or "?"

    @property
    def photo_url(self):
        """Photo envoyée via l'admin, sinon photo par défaut livrée avec le site, sinon chaîne vide."""
        if self.photo:
            return self.photo.url
        return static(DEFAULT_PHOTO) if _static_exists(DEFAULT_PHOTO) else ""

    @property
    def roles_list(self):
        return [role.strip() for role in self.roles.split(",") if role.strip()]

    @property
    def languages_list(self):
        """« Français (C2) · Anglais (B2) » -> ['Français (C2)', 'Anglais (B2)']."""
        return [lang.strip() for lang in self.languages.replace(",", "·").split("·") if lang.strip()]

    @property
    def phone_digits(self):
        """Numéro sans espaces, utilisable dans un lien `tel:`."""
        return "".join(ch for ch in self.phone if ch.isdigit() or ch == "+")

    @property
    def whatsapp_digits(self):
        """Chiffres uniquement, format attendu par `https://wa.me/<numéro>`."""
        return "".join(ch for ch in self.whatsapp if ch.isdigit())

    @property
    def social_links(self):
        """Liens sociaux renseignés : [(nom d'icône, libellé, url), ...]."""
        candidates = [
            ("github", "GitHub", self.github_url),
            ("linkedin", "LinkedIn", self.linkedin_url),
            ("facebook", "Facebook", self.facebook_url),
            ("youtube", "YouTube", self.youtube_url),
        ]
        return [(icon, label, url) for icon, label, url in candidates if url]


class Service(models.Model):
    """Prestation proposée (section « Services » de la page d'accueil)."""

    class Icon(models.TextChoices):
        CODE = "code", _("Développement")
        DATABASE = "database", _("Base de données")
        NETWORK = "network", _("Réseau / serveur")
        CAMERA = "camera", _("Vidéosurveillance")
        SHIELD = "shield", _("Cybersécurité")
        BOOK = "book", _("Formation")
        TOOL = "tool", _("Support / maintenance")

    title = models.CharField("titre", max_length=120)
    description = models.TextField("description")
    icon = models.CharField("icône", max_length=20, choices=Icon.choices, default=Icon.CODE)
    order = models.PositiveSmallIntegerField("ordre", default=0)
    is_published = models.BooleanField("publié", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "service"
        verbose_name_plural = "services"

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """Avis client / apprenant. La section n'apparaît que s'il en existe au moins un publié."""

    author_name = models.CharField("auteur", max_length=120)
    author_role = models.CharField("fonction / contexte", max_length=160, blank=True)
    content = models.TextField("témoignage")
    order = models.PositiveSmallIntegerField("ordre", default=0)
    is_published = models.BooleanField("publié", default=True)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "témoignage"
        verbose_name_plural = "témoignages"

    def __str__(self):
        return f"{self.author_name}"


class FAQ(models.Model):
    question = models.CharField("question", max_length=255)
    answer = models.TextField("réponse")
    order = models.PositiveSmallIntegerField("ordre", default=0)
    is_published = models.BooleanField("publié", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "question fréquente"
        verbose_name_plural = "questions fréquentes (FAQ)"

    def __str__(self):
        return self.question


class Skill(models.Model):
    class Category(models.TextChoices):
        LANGUAGES = "languages", _("Langages de programmation")
        WEB = "web", _("Développement web")
        DATA = "data", _("Bases de données & données")
        SYSTEMS = "systems", _("Réseaux & systèmes")
        SECURITY = "security", _("Cybersécurité")
        TOOLS = "tools", _("Outils & méthodes")

    name = models.CharField("compétence", max_length=80)
    category = models.CharField("catégorie", max_length=20, choices=Category.choices)
    level = models.PositiveSmallIntegerField(
        "niveau (%)", default=70, validators=[MaxValueValidator(100)]
    )
    order = models.PositiveSmallIntegerField("ordre", default=0)

    class Meta:
        ordering = ["category", "order", "name"]
        verbose_name = "compétence"
        verbose_name_plural = "compétences"

    def __str__(self):
        return f"{self.name} ({self.level}%)"


class TimelineItem(models.Model):
    """Élément du parcours : expérience, formation ou certification."""

    class Kind(models.TextChoices):
        EXPERIENCE = "experience", _("Expérience professionnelle")
        EDUCATION = "education", _("Formation")
        CERTIFICATION = "certification", _("Certification")

    kind = models.CharField("type", max_length=20, choices=Kind.choices)
    title = models.CharField("intitulé", max_length=160)
    organization = models.CharField("organisme / entreprise", max_length=160, blank=True)
    period = models.CharField("période", max_length=60, blank=True, help_text="Ex. : 2024 – 2026")
    description = models.TextField("description", blank=True)
    order = models.PositiveSmallIntegerField("ordre", default=0)

    class Meta:
        ordering = ["kind", "order", "-id"]
        verbose_name = "élément du parcours"
        verbose_name_plural = "parcours (expériences, formations, certifications)"

    def __str__(self):
        return f"{self.get_kind_display()} — {self.title}"


class Project(models.Model):
    title = models.CharField("titre", max_length=140)
    description = models.TextField("description")
    technologies = models.CharField(
        "technologies", max_length=255, help_text="Séparées par des virgules. Ex. : Python, Django, PostgreSQL"
    )
    github_url = models.URLField("lien GitHub", blank=True)
    demo_url = models.URLField("lien de démonstration", blank=True)
    screenshot = models.ImageField(
        "image principale",
        upload_to="projects/",
        blank=True,
        help_text="Capture ou photo du projet (recommandé : 1600×1000 px, paysage). Affichée sur la carte portfolio.",
    )
    featured = models.BooleanField(
        "mis en avant",
        default=False,
        help_text="Affiche ce projet en grand en haut de la section Portfolio.",
    )
    order = models.PositiveSmallIntegerField("ordre", default=0, help_text="Plus petit = affiché en premier.")
    created_at = models.DateTimeField("créé le", auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "projet"
        verbose_name_plural = "projets"

    def __str__(self):
        return self.title

    @property
    def tech_list(self):
        return [t.strip() for t in self.technologies.split(",") if t.strip()]

    @property
    def cover_url(self):
        """Image principale, sinon première image de la galerie du projet."""
        if self.screenshot:
            return self.screenshot.url
        first = self.images.first()
        return first.image.url if first else ""


class ProjectImage(models.Model):
    """Photos / captures supplémentaires d'un projet (galerie sous l'image principale)."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images", verbose_name="projet"
    )
    image = models.ImageField(
        "image",
        upload_to="projects/gallery/",
        help_text="Photo ou capture supplémentaire (recommandé : 1600×1000 px).",
    )
    caption = models.CharField("légende", max_length=160, blank=True)
    order = models.PositiveSmallIntegerField("ordre", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "image de projet"
        verbose_name_plural = "images de projet"

    def __str__(self):
        return self.caption or f"Image — {self.project.title}"


class GalleryPhoto(models.Model):
    """
    Photos professionnelles du site (section Galerie) : portrait, atelier, formations,
    interventions… indépendantes des projets.
    """

    class Kind(models.TextChoices):
        PORTRAIT = "portrait", _("Portrait / profil")
        WORK = "work", _("Travail / atelier")
        EVENT = "event", _("Formation / événement")
        OTHER = "other", _("Autre")

    title = models.CharField("titre", max_length=120)
    image = models.ImageField(
        "photo",
        upload_to="gallery/",
        help_text="Photo nette et professionnelle (recommandé : 1200×900 px ou plus).",
    )
    caption = models.CharField(
        "légende",
        max_length=200,
        blank=True,
        help_text="Courte description affichée sous la photo.",
    )
    kind = models.CharField("type", max_length=20, choices=Kind.choices, default=Kind.WORK)
    order = models.PositiveSmallIntegerField("ordre", default=0)
    is_published = models.BooleanField("publié", default=True)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "photo (galerie)"
        verbose_name_plural = "galerie photos"

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField("nom", max_length=120)
    email = models.EmailField("e-mail")
    subject = models.CharField("sujet", max_length=160)
    message = models.TextField("message")
    created_at = models.DateTimeField("reçu le", auto_now_add=True)
    is_read = models.BooleanField("lu", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "message de contact"
        verbose_name_plural = "messages de contact"

    def __str__(self):
        return f"{self.name} — {self.subject}"
