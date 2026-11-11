from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order, Review

# Moyens de paiement proposés au client (hors « gratuit » et « manuel »).
PAYMENT_CHOICES = [
    (value, label)
    for value, label in Order.PaymentMethod.choices
    if value not in {Order.PaymentMethod.FREE, Order.PaymentMethod.MANUAL}
]


class CheckoutForm(forms.Form):
    payment_method = forms.ChoiceField(
        label=_("Moyen de paiement"),
        choices=PAYMENT_CHOICES,
        initial=Order.PaymentMethod.MOBILE_MONEY,
        widget=forms.RadioSelect,
    )


class ReviewForm(forms.ModelForm):
    """Avis sur un cours. La note est choisie via les étoiles du template (boutons radio 1 à 5)."""

    rating = forms.TypedChoiceField(
        label=_("Note"),
        choices=[(value, str(value)) for value in range(5, 0, -1)],
        coerce=int,
        error_messages={"required": _("Choisissez une note de 1 à 5 étoiles.")},
    )

    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "maxlength": 1000,
                    "placeholder": _("Ce que vous avez aimé, ce qui pourrait être amélioré…"),
                }
            )
        }
        labels = {"comment": _("Votre commentaire (facultatif)")}
