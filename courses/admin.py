import csv

from django.contrib import admin, messages
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from modeltranslation.admin import TranslationAdmin

from .models import Course, Order, Review


def _csv_safe(value):
    """Neutralise l'« injection de formule » : Excel exécute les cellules commençant par = + - @."""
    text = "" if value is None else str(value)
    return f"'{text}" if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@admin.register(Course)
class CourseAdmin(TranslationAdmin):
    list_display = ("title", "level", "price", "sales_count", "is_featured", "is_published", "created_at")
    list_filter = ("is_published", "is_featured", "level")
    list_editable = ("price", "is_featured", "is_published")
    search_fields = ("title", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    fieldsets = (
        ("Présentation", {"fields": ("title", "slug", "short_description", "description", "image")}),
        ("Pédagogie", {"fields": ("level", "duration", "learning_outcomes", "requirements")}),
        ("Contenu (réservé aux acheteurs)", {"fields": ("course_file", "course_url")}),
        ("Vente & publication", {"fields": ("price", "is_published", "is_featured")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _sales=Count("orders", filter=Q(orders__status=Order.Status.PAID))
        )

    @admin.display(description="Ventes", ordering="_sales")
    def sales_count(self, obj):
        return obj._sales


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("short_reference", "user", "course", "amount", "status", "payment_method", "paid_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("reference", "user__username", "user__email", "course__title")
    readonly_fields = ("reference", "created_at", "paid_at")
    autocomplete_fields = ("user", "course")
    date_hierarchy = "created_at"
    actions = ["mark_as_paid", "export_csv"]

    @admin.display(description="Référence")
    def short_reference(self, obj):
        return obj.short_reference

    @admin.action(description="Marquer les commandes sélectionnées comme payées (validation manuelle)")
    def mark_as_paid(self, request, queryset):
        done = skipped = 0
        for order in queryset.exclude(status=Order.Status.PAID):
            if not order.payment_method:
                order.payment_method = Order.PaymentMethod.MANUAL
            try:
                with transaction.atomic():
                    order.mark_paid()
                done += 1
            except IntegrityError:
                # L'utilisateur possède déjà ce cours (commande payée existante).
                skipped += 1
        self.message_user(request, f"{done} commande(s) marquée(s) comme payée(s).", messages.SUCCESS)
        if skipped:
            self.message_user(
                request,
                f"{skipped} commande(s) ignorée(s) : l'utilisateur possède déjà ce cours.",
                messages.WARNING,
            )

    @admin.action(description="Exporter la sélection en CSV (Excel)")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="commandes.csv"'
        response.write("\ufeff")  # BOM : Excel reconnaît l'UTF-8 (accents)
        writer = csv.writer(response, delimiter=";")
        writer.writerow(["Référence", "Date", "Client", "E-mail", "Cours", "Montant", "Statut", "Paiement"])
        for o in queryset.select_related("user", "course"):
            writer.writerow(
                [
                    o.short_reference,
                    o.created_at.strftime("%Y-%m-%d %H:%M"),
                    _csv_safe(o.user.get_username()),
                    _csv_safe(o.user.email),
                    _csv_safe(o.course.title),
                    o.amount,
                    o.get_status_display(),
                    o.get_payment_method_display(),
                ]
            )
        return response


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Modération : décochez « approuvé » pour masquer un avis sans le supprimer."""

    list_display = ("course", "user", "rating", "short_comment", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "course")
    list_editable = ("is_approved",)
    search_fields = ("comment", "user__username", "user__email", "course__title")
    readonly_fields = ("course", "user", "created_at", "updated_at")
    date_hierarchy = "created_at"

    @admin.display(description="Commentaire")
    def short_comment(self, obj):
        return (obj.comment[:60] + "…") if len(obj.comment) > 60 else obj.comment

    def has_add_permission(self, request):
        return False  # un avis ne peut venir que d'un acheteur, via le site
