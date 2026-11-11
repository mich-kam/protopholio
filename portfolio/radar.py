"""
Graphique radar des compétences, en SVG pur (aucune bibliothèque JavaScript).

Chaque catégorie de compétences devient un axe ; la distance au centre est la moyenne
des niveaux de la catégorie. Toutes les coordonnées sont calculées ici, le template n'a
plus qu'à les afficher.
"""

import math
from collections import defaultdict

from django.utils.translation import gettext_lazy as _

from .models import Skill

SIZE = 340  # côté du viewBox (carré)
CENTER = SIZE / 2
RADIUS = 105  # rayon du cercle de 100 %
LABEL_RADIUS = RADIUS + 26
RINGS = (25, 50, 75, 100)
MIN_AXES = 3  # en dessous, un radar n'a pas de sens (ligne ou point)

SHORT_LABELS = {
    Skill.Category.LANGUAGES: _("Langages"),
    Skill.Category.WEB: _("Web"),
    Skill.Category.DATA: _("Données"),
    Skill.Category.SYSTEMS: _("Réseaux"),
    Skill.Category.SECURITY: _("Sécurité"),
    Skill.Category.TOOLS: _("Méthodes"),
}


def _point(angle, radius):
    return CENTER + radius * math.cos(angle), CENTER + radius * math.sin(angle)


def _n(value):
    """
    Nombre -> chaîne avec POINT décimal.

    Indispensable en SVG : le site est en français et Django afficherait « 283,4 » dans un attribut.
    Or en SVG la virgule sépare les éléments d'une liste (x="283,4" = deux positions : 283 puis 4),
    ce qui disperse les lettres d'un texte et casse les lignes et les cercles.
    """
    return f"{value:.1f}"


def _fmt(points):
    return " ".join(f"{_n(x)},{_n(y)}" for x, y in points)


def build_radar(skills):
    """Retourne un dict prêt pour le template, ou None s'il y a moins de MIN_AXES catégories."""
    levels = defaultdict(list)
    for skill in skills:
        levels[skill.category].append(skill.level)

    # Ordre des catégories = ordre de déclaration dans le modèle (stable et logique).
    categories = [c for c in Skill.Category.values if levels.get(c)]
    if len(categories) < MIN_AXES:
        return None

    count = len(categories)
    axes, labels, data_points = [], [], []
    for index, category in enumerate(categories):
        angle = -math.pi / 2 + index * 2 * math.pi / count  # le premier axe pointe vers le haut
        average = sum(levels[category]) / len(levels[category])
        ax, ay = _point(angle, RADIUS)
        dx, dy = _point(angle, RADIUS * average / 100)
        lx, ly = _point(angle, LABEL_RADIUS)
        axes.append({"x": _n(ax), "y": _n(ay)})
        data_points.append((dx, dy))
        cos = math.cos(angle)
        labels.append(
            {
                "x": _n(lx),
                "y": _n(ly + 4),  # +4 : centre visuel du texte
                "anchor": "middle" if abs(cos) < 0.25 else ("start" if cos > 0 else "end"),
                "text": SHORT_LABELS.get(category, category),
                "value": round(average),
            }
        )

    rings = [_fmt(_point(-math.pi / 2 + i * 2 * math.pi / count, RADIUS * pct / 100) for i in range(count)) for pct in RINGS]
    return {
        "size": SIZE,
        "center": _n(CENTER),
        "rings": rings,
        "axes": axes,
        "labels": labels,
        "polygon": _fmt(data_points),
        "dots": [{"x": _n(x), "y": _n(y)} for x, y in data_points],
    }
