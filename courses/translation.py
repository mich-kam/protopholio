"""Champs traduisibles des cours (voir portfolio/translation.py pour le principe)."""

from modeltranslation.translator import TranslationOptions, register

from .models import Course


@register(Course)
class CourseTranslationOptions(TranslationOptions):
    fields = ("title", "short_description", "description", "duration", "learning_outcomes", "requirements")
