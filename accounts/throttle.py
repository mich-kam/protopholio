"""
Limitation des tentatives de connexion (protection contre le brute-force).

Règle : MAX_FAILURES échecs en moins de WINDOW pour un même identifiant => connexion bloquée
jusqu'à ce que les plus anciens échecs sortent de la fenêtre. Un succès remet le compteur à zéro.

Compromis assumé : le blocage porte sur l'IDENTIFIANT (et non sur l'adresse IP). Derrière le proxy
d'une plateforme (Render, Heroku...) l'IP vue par Django est celle du proxy : bloquer par IP
verrouillerait TOUS les visiteurs d'un coup. Contrepartie : quelqu'un peut gêner temporairement
la connexion d'une personne précise ; celle-ci garde la réinitialisation par e-mail.
"""

from datetime import timedelta
from math import ceil

from django.utils import timezone

from .models import FailedLogin

MAX_FAILURES = 5
WINDOW = timedelta(minutes=15)


def _key(identifier):
    return (identifier or "").strip().lower()[:150]


def _recent(identifier):
    return FailedLogin.objects.filter(identifier=_key(identifier), created_at__gte=timezone.now() - WINDOW)


def is_locked(identifier):
    key = _key(identifier)
    return bool(key) and _recent(key).count() >= MAX_FAILURES


def minutes_remaining(identifier):
    """Minutes (arrondies au supérieur) avant la fin du blocage ; 0 si l'identifiant n'est pas bloqué."""
    attempts = list(_recent(identifier).order_by("created_at").values_list("created_at", flat=True))
    if len(attempts) < MAX_FAILURES:
        return 0
    # Le blocage cesse quand assez d'échecs ont expiré pour repasser sous le seuil.
    unlock_at = attempts[len(attempts) - MAX_FAILURES] + WINDOW
    return max(1, ceil((unlock_at - timezone.now()).total_seconds() / 60))


def record_failure(identifier):
    key = _key(identifier)
    if not key or is_locked(key):
        return  # déjà bloqué : on n'allonge pas le blocage à chaque nouvel essai
    FailedLogin.objects.create(identifier=key)
    # Ménage : on ne garde pas d'historique inutile.
    FailedLogin.objects.filter(created_at__lt=timezone.now() - 2 * WINDOW).delete()


def clear(*identifiers):
    keys = {_key(i) for i in identifiers if i}
    if keys:
        FailedLogin.objects.filter(identifier__in=keys).delete()
