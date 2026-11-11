"""Champs traduisibles des articles (voir portfolio/translation.py pour le principe)."""

from modeltranslation.translator import TranslationOptions, register

from .models import Post


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ("title", "excerpt", "content", "tags")
