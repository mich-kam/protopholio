import os
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.views.decorators.http import require_http_methods, require_POST

from portfolio.seo import jsonld

from . import payments
from .emails import send_order_confirmation
from .forms import CheckoutForm, ReviewForm
from .models import Course, Order, Review

COURSES_PER_PAGE = 9
RELATED_COURSES = 3

# Clé d'URL -> (libellé affiché, ordre SQL)
SORTS = {
    "featured": (gettext_lazy("À la une"), ["-is_featured", "-created_at"]),
    "recent": (gettext_lazy("Plus récents"), ["-created_at"]),
    "price_asc": (gettext_lazy("Prix croissant"), ["price", "-created_at"]),
    "price_desc": (gettext_lazy("Prix décroissant"), ["-price", "-created_at"]),
    "title": (gettext_lazy("Titre (A → Z)"), ["title"]),
}
DEFAULT_SORT = "featured"


def owned_course_ids(user):
    """Ensemble des ids de cours déjà achetés (pastille « Acquis » sur les cartes)."""
    if not user.is_authenticated:
        return set()
    return set(
        Order.objects.filter(user=user, status=Order.Status.PAID).values_list("course_id", flat=True)
    )


def course_list(request):
    """Catalogue : recherche, filtres (niveau, prix), tri et pagination."""
    q = request.GET.get("q", "").strip()[:100]
    level = request.GET.get("niveau", "")
    price = request.GET.get("prix", "")
    sort = request.GET.get("tri", DEFAULT_SORT)
    if sort not in SORTS:
        sort = DEFAULT_SORT

    courses = Course.objects.published().with_ratings()
    if q:
        courses = courses.filter(
            Q(title__icontains=q) | Q(short_description__icontains=q) | Q(description__icontains=q)
        )
    if level in Course.Level.values:
        courses = courses.filter(level=level)
    else:
        level = ""
    if price == "free":
        courses = courses.filter(price=0)
    elif price == "paid":
        courses = courses.filter(price__gt=0)
    else:
        price = ""
    courses = courses.order_by(*SORTS[sort][1])

    paginator = Paginator(courses, COURSES_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "courses/course_list.html",
        {
            "courses": page_obj,
            "page_obj": page_obj,
            "total": paginator.count,
            "q": q,
            "level": level,
            "price": price,
            "sort": sort,
            "levels": Course.Level.choices,
            "sorts": [(key, label) for key, (label, _order) in SORTS.items()],
            "has_filters": bool(q or level or price),
            "owned_ids": owned_course_ids(request.user),
        },
    )


def _related_courses(course):
    """Cours similaires : même niveau d'abord, complétés par les autres si besoin."""
    others = Course.objects.published().with_ratings().exclude(pk=course.pk)
    related = list(others.filter(level=course.level)[:RELATED_COURSES])
    if len(related) < RELATED_COURSES:
        picked = [c.pk for c in related]
        related += list(others.exclude(pk__in=picked)[: RELATED_COURSES - len(related)])
    return related


def _rating_summary(course):
    """Moyenne, nombre d'avis et répartition par étoile (avis approuvés uniquement)."""
    approved = course.reviews.filter(is_approved=True)
    totals = approved.aggregate(avg=Avg("rating"), count=Count("id"))
    per_star = {row["rating"]: row["n"] for row in approved.values("rating").annotate(n=Count("id"))}
    count = totals["count"]
    return {
        "avg": round(totals["avg"], 1) if count else None,
        "count": count,
        "bars": [
            {"stars": stars, "n": per_star.get(stars, 0), "pct": round(per_star.get(stars, 0) * 100 / count) if count else 0}
            for stars in range(5, 0, -1)
        ],
    }


def _course_jsonld(request, course, summary):
    data = {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": course.title,
        "description": course.short_description,
        "url": request.build_absolute_uri(course.get_absolute_url()),
        "inLanguage": translation.get_language(),
        "offers": {
            "@type": "Offer",
            "price": str(course.price),
            "priceCurrency": settings.CURRENCY_CODE,
            "availability": "https://schema.org/InStock",
        },
    }
    if summary["count"]:  # uniquement de VRAIS avis : jamais de note inventée
        data["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": summary["avg"],
            "reviewCount": summary["count"],
        }
    return jsonld(data)


def course_detail(request, slug):
    course = get_object_or_404(Course.objects.published().with_ratings(), slug=slug)
    summary = _rating_summary(course)
    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "has_access": course.is_accessible_by(request.user),
            "related_courses": _related_courses(course),
            "owned_ids": owned_course_ids(request.user),
            "rating": summary,
            "reviews": course.reviews.filter(is_approved=True).select_related("user")[:20],
            "jsonld": _course_jsonld(request, course, summary),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request, slug):
    """Récapitulatif de commande puis paiement (SIMULÉ — voir courses/payments.py)."""
    course = get_object_or_404(Course.objects.published(), slug=slug)

    if Order.objects.filter(user=request.user, course=course, status=Order.Status.PAID).exists():
        messages.info(request, _("Vous possédez déjà ce cours."))
        return redirect("courses:access", slug=course.slug)

    form = CheckoutForm(request.POST or None)

    if request.method == "POST" and (course.is_free or form.is_valid()):
        method = (
            Order.PaymentMethod.FREE if course.is_free else form.cleaned_data["payment_method"]
        )
        try:
            with transaction.atomic():
                # On réutilise une éventuelle commande en attente plutôt que d'en empiler.
                order = (
                    Order.objects.filter(user=request.user, course=course, status=Order.Status.PENDING).first()
                    or Order(user=request.user, course=course)
                )
                order.amount = course.price  # prix figé au moment de l'achat
                order.payment_method = method
                order.save()

                paid = payments.charge(order)
                if paid:
                    order.mark_paid()

            if paid:
                send_order_confirmation(order, request)  # hors transaction : l'achat est déjà validé
                messages.success(
                    request,
                    _("Paiement confirmé ! Commande n° %(reference)s. Bon apprentissage !")
                    % {"reference": order.short_reference},
                )
                return redirect("courses:access", slug=course.slug)

            messages.error(request, _("Le paiement a échoué. Veuillez réessayer."))
        except IntegrityError:
            # Double clic / double soumission : la commande payée existe déjà.
            messages.info(request, _("Votre commande a déjà été enregistrée."))
            return redirect("courses:access", slug=course.slug)

    return render(
        request,
        "courses/checkout.html",
        {"course": course, "form": form, "simulated": payments.SIMULATED},
    )


@login_required
def course_access(request, slug):
    """Contenu du cours : réservé aux acheteurs (même si le cours a été dépublié depuis)."""
    course = get_object_or_404(Course, slug=slug)
    if not course.is_accessible_by(request.user):
        messages.warning(request, _("Vous devez acheter ce cours pour y accéder."))
        return redirect("courses:detail", slug=course.slug)
    order = Order.objects.filter(user=request.user, course=course, status=Order.Status.PAID).first()
    my_review = Review.objects.filter(course=course, user=request.user).first()
    return render(
        request,
        "courses/course_access.html",
        {
            "course": course,
            "order": order,
            "can_review": course.has_purchased(request.user),
            "my_review": my_review,
            "review_form": ReviewForm(instance=my_review),
        },
    )


@login_required
@require_POST
def review_submit(request, slug):
    """Publier (ou modifier) son avis. Réservé aux acheteurs : un avis doit refléter une vraie expérience."""
    course = get_object_or_404(Course, slug=slug)
    if not course.has_purchased(request.user):
        messages.warning(request, _("Seuls les acheteurs d'un cours peuvent laisser un avis."))
        return redirect("courses:detail", slug=course.slug)

    existing = Review.objects.filter(course=course, user=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.course, review.user = course, request.user  # jamais lus depuis le formulaire
        review.save()  # un avis masqué par la modération le reste après modification
        messages.success(
            request,
            _("Votre avis a été mis à jour.") if existing else _("Merci ! Votre avis a bien été enregistré."),
        )
        return redirect(f"{reverse('courses:access', args=[course.slug])}#avis")

    order = Order.objects.filter(user=request.user, course=course, status=Order.Status.PAID).first()
    return render(
        request,
        "courses/course_access.html",
        {"course": course, "order": order, "can_review": True, "my_review": existing, "review_form": form},
        status=400,
    )


@login_required
def course_download(request, slug):
    """Téléchargement du fichier du cours, protégé par le même contrôle d'accès."""
    course = get_object_or_404(Course, slug=slug)
    if not course.is_accessible_by(request.user):
        messages.warning(request, _("Vous devez acheter ce cours pour le télécharger."))
        return redirect("courses:detail", slug=course.slug)
    if not course.course_file:
        raise Http404("Ce cours n'a pas de fichier.")
    return FileResponse(
        course.course_file.open("rb"),
        as_attachment=True,
        filename=os.path.basename(course.course_file.name),
    )


@login_required
def receipt(request, reference):
    """Reçu imprimable. Réservé au propriétaire de la commande (404 sinon : on ne révèle rien)."""
    order = get_object_or_404(
        Order.objects.select_related("course", "user"), reference=reference, status=Order.Status.PAID
    )
    if order.user_id != request.user.id and not request.user.is_superuser:
        raise Http404
    return render(
        request,
        "courses/receipt.html",
        {"order": order, "simulated": payments.SIMULATED and order.payment_method != Order.PaymentMethod.FREE},
    )


@login_required
def dashboard(request):
    """« Mes cours achetés » — réservé aux utilisateurs connectés."""
    orders = list(
        Order.objects.filter(user=request.user, status=Order.Status.PAID)
        .select_related("course")
        .order_by("-paid_at")
    )
    owned = {o.course_id for o in orders}
    total_spent = sum((o.amount for o in orders), Decimal("0"))
    recommended = list(Course.objects.published().with_ratings().exclude(pk__in=owned)[:3])
    return render(
        request,
        "courses/dashboard.html",
        {
            "orders": orders,
            "total_spent": total_spent,
            "last_order": orders[0] if orders else None,
            "recommended": recommended,
            "owned_ids": owned,
        },
    )
