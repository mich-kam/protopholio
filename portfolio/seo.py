"""Aides SEO : données structurées JSON-LD (schema.org)."""

import json

from django.utils.safestring import mark_safe


def jsonld(data: dict) -> str:
    """
    Sérialise un dict en JSON-LD sûr pour un `<script type="application/ld+json">`.

    On échappe `<`, `>` et `&` en séquences unicode pour qu'aucune valeur (nom, description...)
    ne puisse refermer la balise <script> ni injecter du HTML.
    """
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    raw = raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(raw)  # noqa: S308 - entièrement échappé ci-dessus
