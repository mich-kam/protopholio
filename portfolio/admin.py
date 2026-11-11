from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from .models import (
    FAQ,
    ContactMessage,
    GalleryPhoto,
    Profile,
    Project,
    ProjectImage,
    Service,
    Skill,
    Testimonial,
    TimelineItem,
)

admin.site.site_header = "Administration du portfolio"
admin.site.site_title = "Administration"
admin.site.index_title = "Gérer mon site, mes cours et mes commandes"


@admin.register(Profile)
class ProfileAdmin(TranslationAdmin):
    list_display = ("full_name", "headline", "email", "available_for_work")
    fieldsets = (
        (
            "Identité & photo",
            {
                "description": "Ajoutez ici votre photo de profil : elle apparaît en page d'accueil (hero + À propos).",
                "fields": ("full_name", "headline", "roles", "tagline", "photo", "available_for_work"),
            },
        ),
        ("Présentation", {"fields": ("about", "languages", "cv_file")}),
        ("Coordonnées", {"fields": ("email", "phone", "whatsapp", "location")}),
        ("Réseaux sociaux", {"fields": ("github_url", "linkedin_url", "facebook_url", "youtube_url")}),
    )

    def has_add_permission(self, request):
        # Une seule fiche de profil.
        return not Profile.objects.exists()


@admin.register(Service)
class ServiceAdmin(TranslationAdmin):
    list_display = ("title", "icon", "order", "is_published")
    list_editable = ("order", "is_published")


@admin.register(Skill)
class SkillAdmin(TranslationAdmin):
    list_display = ("name", "category", "level", "order")
    list_filter = ("category",)
    list_editable = ("level", "order")
    search_fields = ("name",)


@admin.register(TimelineItem)
class TimelineItemAdmin(TranslationAdmin):
    list_display = ("title", "organization", "kind", "period", "order")
    list_filter = ("kind",)
    list_editable = ("order",)
    search_fields = ("title", "organization")


class ProjectImageInline(TranslationTabularInline):
    model = ProjectImage
    extra = 2
    fields = ("image", "caption", "order")
    ordering = ("order", "id")


@admin.register(Project)
class ProjectAdmin(TranslationAdmin):
    list_display = ("title", "technologies", "featured", "order", "created_at")
    list_filter = ("featured",)
    list_editable = ("featured", "order")
    search_fields = ("title", "technologies", "description")
    inlines = [ProjectImageInline]
    fieldsets = (
        (
            "Projet",
            {
                "description": "Chaque projet apparaît dans la section Portfolio. Cochez « mis en avant » "
                "pour l'afficher en grand.",
                "fields": ("title", "description", "technologies", "featured", "order"),
            },
        ),
        (
            "Image principale",
            {
                "description": "Obligatoire pour un rendu professionnel. Ajoutez d'autres photos ci-dessous "
                "(Images de projet).",
                "fields": ("screenshot",),
            },
        ),
        ("Liens", {"fields": ("github_url", "demo_url")}),
    )


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(TranslationAdmin):
    list_display = ("title", "kind", "order", "is_published")
    list_filter = ("kind", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("title", "caption")
    fieldsets = (
        (
            None,
            {
                "description": "Ces photos alimentent la section « Galerie » de la page d'accueil "
                "(portrait, atelier, formations…).",
                "fields": ("title", "image", "caption", "kind", "order", "is_published"),
            },
        ),
    )


@admin.register(Testimonial)
class TestimonialAdmin(TranslationAdmin):
    list_display = ("author_name", "author_role", "order", "is_published")
    list_editable = ("order", "is_published")


@admin.register(FAQ)
class FAQAdmin(TranslationAdmin):
    list_display = ("question", "order", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("question", "answer")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    list_editable = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")

    def has_add_permission(self, request):
        return False
