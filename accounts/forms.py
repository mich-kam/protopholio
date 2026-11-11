from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from . import throttle

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Connexion avec le nom d'utilisateur OU l'adresse e-mail, avec message clair en cas de blocage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Nom d’utilisateur ou e-mail")
        self.fields["username"].widget.attrs.update({"autocomplete": "username", "autofocus": True})
        self.fields["password"].widget.attrs.update({"autocomplete": "current-password"})

    def clean(self):
        username = self.cleaned_data.get("username")
        if username and throttle.is_locked(username):
            minutes = throttle.minutes_remaining(username)
            raise forms.ValidationError(
                ngettext(
                    "Trop de tentatives échouées. Par sécurité, la connexion est bloquée pendant "
                    "encore %(minutes)d minute. Vous pouvez aussi réinitialiser votre mot de passe.",
                    "Trop de tentatives échouées. Par sécurité, la connexion est bloquée pendant "
                    "encore %(minutes)d minutes. Vous pouvez aussi réinitialiser votre mot de passe.",
                    minutes,
                ),
                code="locked",
                params={"minutes": minutes},
            )
        return super().clean()


class RegisterForm(UserCreationForm):
    """Formulaire d'inscription : nom d'utilisateur, e-mail et mot de passe."""

    email = forms.EmailField(label=_("Adresse e-mail"))

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Un compte existe déjà avec cette adresse e-mail."))
        return email


class ProfileForm(forms.ModelForm):
    """Modification des informations personnelles du compte."""

    email = forms.EmailField(label=_("Adresse e-mail"))

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {"first_name": _("Prénom"), "last_name": _("Nom")}

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("Cette adresse e-mail est déjà utilisée par un autre compte."))
        return email
