import uuid
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


def course_file_path(instance, filename):
    """
    Les fichiers de cours sont rangés dans un sous-dossier aléatoire : même si
    quelqu'un devinait le nom du fichier, l'URL reste introuvable. Surtout, ce
    dossier n'est jamais servi publiquement (voir config/urls.py).
    """
    return f"courses/files/{uuid.uuid4().hex}/{filename}"


class CourseQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def with_ratings(self):
        """Ajoute `avg_rating` et `rating_count` (avis approuvés uniquement), calculés en une seule requête."""
        approved = models.Q(reviews__is_approved=True)
        return self.annotate(
            avg_rating=models.Avg("reviews__rating", filter=approved),
            rating_count=models.Count("reviews", filter=approved),
        )


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", _("Débutant")
        INTERMEDIATE = "intermediate", _("Intermédiaire")
        ADVANCED = "advanced", _("Avancé")

    title = models.CharField("titre", max_length=160)
    slug = models.SlugField("slug (URL)", max_length=180, unique=True, blank=True)
    short_description = models.CharField("résumé", max_length=255)
    description = models.TextField("description détaillée")
    level = models.CharField("niveau", max_length=20, choices=Level.choices, default=Level.BEGINNER)
    duration = models.CharField(
        "durée", max_length=60, blank=True, help_text="Ex. : 6 h de contenu · 12 leçons"
    )
    learning_outcomes = models.TextField(
        "ce que vous allez apprendre",
        blank=True,
        help_text="Un point par ligne.",
    )
    requirements = models.TextField("prérequis", blank=True, help_text="Un point par ligne.")
    price = models.DecimalField(
        "prix",
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="0 = cours gratuit.",
    )
    image = models.ImageField("image de couverture", upload_to="courses/images/", blank=True)
    course_file = models.FileField(
        "fichier du cours",
        upload_to=course_file_path,
        blank=True,
        help_text="PDF, ZIP, etc. Accessible uniquement aux acheteurs.",
    )
    course_url = models.URLField(
        "lien du cours",
        blank=True,
        help_text="Vidéo, Google Drive, Notion... Visible uniquement par les acheteurs.",
    )
    is_published = models.BooleanField("publié", default=True)
    is_featured = models.BooleanField(
        "mis en avant", default=False, help_text="Affiché en premier dans les listes."
    )
    created_at = models.DateTimeField("créé le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    objects = CourseQuerySet.as_manager()

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        verbose_name = "cours"
        verbose_name_plural = "cours"

    def __str__(self):
        return self.title

    def clean(self):
        if self.is_published and not (self.course_file or self.course_url):
            raise ValidationError(
                "Un cours publié doit avoir un fichier ou un lien d'accès (sinon décochez « publié »)."
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "cours"
            slug, n = base, 2
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("courses:detail", kwargs={"slug": self.slug})

    @property
    def is_free(self):
        return self.price == 0

    @property
    def is_new(self):
        """Vrai pour un cours publié depuis moins de 30 jours (pastille « Nouveau »)."""
        return self.created_at >= timezone.now() - timedelta(days=30)

    @staticmethod
    def _lines(text):
        return [line.strip(" -•\t") for line in text.splitlines() if line.strip(" -•\t")]

    @property
    def outcomes_list(self):
        return self._lines(self.learning_outcomes)

    @property
    def requirements_list(self):
        return self._lines(self.requirements)

    def has_purchased(self, user):
        """Vrai si l'utilisateur a réellement acheté ce cours (les super-utilisateurs ne comptent pas)."""
        return user.is_authenticated and self.orders.filter(user=user, status=Order.Status.PAID).exists()

    def is_accessible_by(self, user):
        """Vrai si l'utilisateur a acheté ce cours (ou est super-utilisateur : aperçu)."""
        if not user.is_authenticated:
            return False
        return user.is_superuser or self.has_purchased(user)


class Order(models.Model):
    """Commande : relie un utilisateur à un cours (l'accès = une commande PAYÉE)."""

    class Status(models.TextChoices):
        PENDING = "pending", _("En attente")
        PAID = "paid", _("Payée")
        CANCELLED = "cancelled", _("Annulée")

    class PaymentMethod(models.TextChoices):
        MOBILE_MONEY = "mobile_money", _("Mobile Money (simulation)")
        CARD = "card", _("Carte bancaire (simulation)")
        PAYPAL = "paypal", _("PayPal (simulation)")
        FREE = "free", _("Cours gratuit")
        MANUAL = "manual", _("Validation manuelle")

    reference = models.UUIDField("référence", default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders", verbose_name="utilisateur"
    )
    # PROTECT : on ne peut pas supprimer un cours déjà vendu (dépubliez-le plutôt).
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name="orders", verbose_name="cours"
    )
    amount = models.DecimalField("montant", max_digits=8, decimal_places=2)
    status = models.CharField("statut", max_length=12, choices=Status.choices, default=Status.PENDING)
    payment_method = models.CharField(
        "moyen de paiement", max_length=20, choices=PaymentMethod.choices, blank=True
    )
    created_at = models.DateTimeField("créée le", auto_now_add=True)
    paid_at = models.DateTimeField("payée le", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "commande"
        verbose_name_plural = "commandes"
        constraints = [
            # Un utilisateur ne peut acheter un même cours qu'une seule fois.
            models.UniqueConstraint(
                fields=["user", "course"],
                condition=models.Q(status="paid"),
                name="unique_paid_order_per_user_course",
            )
        ]

    def __str__(self):
        return f"Commande {self.short_reference} — {self.user} → {self.course}"

    @property
    def short_reference(self):
        """Référence lisible affichée au client (8 premiers caractères en majuscules)."""
        return str(self.reference)[:8].upper()

    def mark_paid(self):
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at", "payment_method", "amount"])


class Review(models.Model):
    """Avis d'un acheteur sur un cours : une note de 1 à 5 et un commentaire facultatif."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews", verbose_name="cours")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews", verbose_name="utilisateur"
    )
    rating = models.PositiveSmallIntegerField(
        "note", validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="De 1 à 5 étoiles."
    )
    comment = models.TextField("commentaire", blank=True, max_length=1000)
    is_approved = models.BooleanField(
        "approuvé", default=True, help_text="Décochez pour masquer un avis inapproprié sans le supprimer."
    )
    created_at = models.DateTimeField("publié le", auto_now_add=True)
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "avis"
        verbose_name_plural = "avis"
        constraints = [
            models.UniqueConstraint(fields=["course", "user"], name="one_review_per_user_per_course"),
        ]

    def __str__(self):
        return f"{self.user} — {self.course} ({self.rating}/5)"

    @property
    def author_name(self):
        """Nom affiché publiquement : prénom + initiale du nom (jamais l'e-mail)."""
        first = self.user.first_name.strip()
        last = self.user.last_name.strip()
        if first:
            return f"{first} {last[0]}." if last else first
        return self.user.get_username()
