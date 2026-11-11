"""
Champs de contenu traduisibles (django-modeltranslation).

Chaque champ listé ci-dessous obtient une colonne par langue (title_fr, title_en...). Dans le code et les
templates, on continue d'écrire `service.title` : la valeur renvoyée est celle de la langue active, avec repli
sur le français si la traduction anglaise est vide. Dans l'administration, chaque champ apparaît en deux
versions (Français / English).
"""

from modeltranslation.translator import TranslationOptions, register

from .models import FAQ, GalleryPhoto, Profile, Project, ProjectImage, Service, Skill, Testimonial, TimelineItem


@register(Profile)
class ProfileTranslationOptions(TranslationOptions):
    fields = ("headline", "roles", "tagline", "about", "languages", "location")


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(Skill)
class SkillTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(TimelineItem)
class TimelineItemTranslationOptions(TranslationOptions):
    fields = ("title", "organization", "description")


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ("title", "description", "technologies")


@register(ProjectImage)
class ProjectImageTranslationOptions(TranslationOptions):
    fields = ("caption",)


@register(GalleryPhoto)
class GalleryPhotoTranslationOptions(TranslationOptions):
    fields = ("title", "caption")


@register(Testimonial)
class TestimonialTranslationOptions(TranslationOptions):
    fields = ("author_role", "content")


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ("question", "answer")
