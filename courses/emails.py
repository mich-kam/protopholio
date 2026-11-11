import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


def send_order_confirmation(order, request):
    """
    E-mail de confirmation d'achat (lien d'accès + reçu).

    Un échec d'envoi (SMTP indisponible...) ne doit JAMAIS annuler un achat déjà
    enregistré : on journalise l'erreur et on continue.
    """
    user = order.user
    if not user.email:
        return False

    context = {
        "order": order,
        "course": order.course,
        "user": user,
        "access_url": request.build_absolute_uri(reverse("courses:access", args=[order.course.slug])),
        "receipt_url": request.build_absolute_uri(reverse("courses:receipt", args=[order.reference])),
        "CURRENCY_SYMBOL": settings.CURRENCY_SYMBOL,
    }
    try:
        send_mail(
            # La langue active est celle du site où le client a commandé : l'e-mail est rédigé dans cette langue.
            subject=_("Confirmation de votre commande %(reference)s") % {"reference": order.short_reference},
            message=render_to_string("courses/emails/order_confirmation.txt", context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
    except Exception:
        logger.exception("Échec d'envoi de l'e-mail de confirmation (commande %s).", order.short_reference)
        return False
    return True
