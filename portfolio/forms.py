from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")
        labels = {
            "name": _("Votre nom"),
            "email": _("E-mail"),
            "subject": _("Sujet"),
            "message": _("Message"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Votre nom"), "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": _("name@domaine.com"), "autocomplete": "email"}),
            "subject": forms.TextInput(attrs={"placeholder": _("Objet de votre message")}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": _("Comment puis-je vous aider ?")}),
        }
