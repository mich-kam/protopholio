"""
Paiements cours : Flutterwave (carte + Mobile Money) ou simulation locale.

- Sans `FLUTTERWAVE_SECRET_KEY` : mode démo (aucun débit réel).
- Avec la clé : redirection vers le checkout Flutterwave, puis vérification
  au retour (`payment_callback`) avant de marquer la commande comme payée.

Créez un compte sur https://dashboard.flutterwave.com/ et renseignez
FLUTTERWAVE_PUBLIC_KEY / FLUTTERWAVE_SECRET_KEY dans l'environnement.
"""

from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings
from django.urls import reverse

from .models import Order

logger = logging.getLogger(__name__)

FLW_PAYMENTS_URL = "https://api.flutterwave.com/v3/payments"
FLW_VERIFY_URL = "https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"

# Options Flutterwave filtrées selon le choix du client.
METHOD_OPTIONS = {
    Order.PaymentMethod.MOBILE_MONEY: "mobilemoneyfranco,mobilemoneyxaf,mpesa,account,ussd,banktransfer",
    Order.PaymentMethod.CARD: "card",
    Order.PaymentMethod.PAYPAL: "card,account",
}


def _secret() -> str:
    return (getattr(settings, "FLUTTERWAVE_SECRET_KEY", "") or "").strip()


def is_simulated() -> bool:
    """True tant qu'aucune clé secrète Flutterwave n'est configurée."""
    return not bool(_secret())


# Compatibilité templates / tests existants.
SIMULATED = is_simulated()


def charge(order: Order) -> bool:
    """
    Paiement immédiat (gratuit ou simulation).
    Pour un vrai paiement Flutterwave, utiliser `start_checkout()` à la place.
    """
    if order.payment_method == Order.PaymentMethod.FREE or is_simulated():
        return True
    return False


def start_checkout(order: Order, request) -> str | None:
    """
    Crée une session Flutterwave et renvoie l'URL de paiement.
    Retourne None en mode simulation / cours gratuit (le caller marque alors payé).
    """
    if order.payment_method == Order.PaymentMethod.FREE or is_simulated():
        return None

    callback = request.build_absolute_uri(reverse("courses:payment_callback"))
    currency = getattr(settings, "CURRENCY_CODE", "USD") or "USD"
    options = METHOD_OPTIONS.get(order.payment_method, "card,mobilemoneyfranco,account")
    customer_name = order.user.get_full_name() or order.user.username
    payload = {
        "tx_ref": str(order.reference),
        "amount": float(order.amount),
        "currency": currency,
        "redirect_url": callback,
        "payment_options": options,
        "customer": {
            "email": order.user.email or f"user{order.user_id}@ir-kamango-mich.onrender.com",
            "name": customer_name,
        },
        "customizations": {
            "title": order.course.title[:50],
            "description": f"Commande {order.short_reference}",
        },
        "meta": {
            "order_reference": str(order.reference),
            "course_slug": order.course.slug,
            "user_id": order.user_id,
        },
    }

    response = requests.post(
        FLW_PAYMENTS_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {_secret()}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    try:
        data = response.json()
    except ValueError:
        logger.error("Flutterwave: réponse non JSON (%s)", response.status_code)
        raise RuntimeError("Le service de paiement est indisponible. Réessayez plus tard.")

    if response.status_code >= 400 or data.get("status") != "success":
        message = data.get("message") or f"HTTP {response.status_code}"
        logger.error("Flutterwave initiate failed: %s", message)
        raise RuntimeError(message)

    link = (data.get("data") or {}).get("link")
    if not link:
        raise RuntimeError("Lien de paiement manquant.")
    return link


def verify_transaction(transaction_id: str) -> dict[str, Any] | None:
    """Vérifie une transaction Flutterwave. Retourne le payload `data` si successful."""
    if not transaction_id or is_simulated():
        return None
    response = requests.get(
        FLW_VERIFY_URL.format(transaction_id=transaction_id),
        headers={"Authorization": f"Bearer {_secret()}"},
        timeout=30,
    )
    try:
        body = response.json()
    except ValueError:
        logger.error("Flutterwave verify: réponse non JSON")
        return None
    if body.get("status") != "success":
        logger.warning("Flutterwave verify status=%s msg=%s", body.get("status"), body.get("message"))
        return None
    data = body.get("data") or {}
    if data.get("status") != "successful":
        return None
    return data
