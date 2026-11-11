"""Rendu Markdown sécurisé pour les articles."""

import markdown
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = {
    "p", "br", "hr", "h2", "h3", "h4", "strong", "em", "b", "i", "ul", "ol", "li", "blockquote",
    "code", "pre", "a", "img", "table", "thead", "tbody", "tr", "th", "td", "del",
}  # fmt: skip
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title"},
    "h2": {"id"},
    "h3": {"id"},
    "h4": {"id"},
    "code": {"class"},
}
ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}


@register.filter(name="markdown_safe")
def markdown_safe(text):
    """
    Markdown -> HTML, puis NETTOYAGE : tout ce qui n'est pas dans la liste blanche (balises <script>,
    <iframe>, attributs onclick=..., liens javascript:...) est supprimé. Le résultat peut donc être
    affiché sans risque d'injection (XSS), même si un contenu malveillant était collé dans l'admin.
    """
    html = markdown.markdown(
        text or "",
        extensions=["extra", "sane_lists", "toc"],
        extension_configs={"toc": {"toc_depth": "2-4"}},
    )
    cleaned = nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
        link_rel="noopener noreferrer",
    )
    return mark_safe(cleaned)  # noqa: S308 - nettoyé par nh3 ci-dessus
