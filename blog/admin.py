from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Post


@admin.register(Post)
class PostAdmin(TranslationAdmin):
    list_display = ("title", "published_at", "is_published", "is_featured", "reading_time_display")
    list_filter = ("is_published", "is_featured", "published_at")
    list_editable = ("is_published", "is_featured")
    search_fields = ("title", "excerpt", "content", "tags")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    fieldsets = (
        ("Article", {"fields": ("title", "slug", "excerpt", "cover", "tags")}),
        ("Contenu", {"fields": ("content",)}),
        ("Publication", {"fields": ("is_published", "is_featured", "published_at")}),
    )

    @admin.display(description="Lecture")
    def reading_time_display(self, obj):
        return f"{obj.reading_time} min"
