"""
Couche de paiement.

Aujourd'hui : SIMULATION (aucun argent réel n'est débité).
Pour passer à un vrai paiement, remplacez le corps de `charge()` par un appel
à Stripe Checkout / PayPal / un agrégateur Mobile Money, retournez True
uniquement quand le paiement est confirmé, puis passez SIMULATED à False :
les mentions « mode démonstration » disparaissent du site et des reçus.
Le reste de l'application (vues, accès aux cours, tableau de bord) ne change pas.
(Pensez aussi à retirer « (simulation) » des libellés de `Order.PaymentMethod`.)
"""

from .models import Order

# Pilote l'affichage des bandeaux « mode démonstration » (paiement, reçu).
SIMULATED = True


def charge(order: Order) -> bool:
    """Tente de débiter la commande. Retourne True si le paiement est confirmé."""
    # Simulation : tout paiement réussit.
    return True
