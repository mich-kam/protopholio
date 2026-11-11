from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from . import views
from .forms import LoginForm

app_name = "accounts"

# Segments traduits : /comptes/connexion/  <->  /en/accounts/login/
urlpatterns = [
    path(_("inscription/"), views.register, name="register"),
    path(
        _("connexion/"),
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    # Depuis Django 5, la déconnexion exige une requête POST (protection CSRF).
    path(_("deconnexion/"), auth_views.LogoutView.as_view(), name="logout"),
    # Mon compte
    path(_("profil/"), views.profile, name="profile"),
    path(_("mot-de-passe/modifier/"), views.PasswordChangeViewFr.as_view(), name="password_change"),
    # Mot de passe oublié (le lien est envoyé par e-mail)
    path(
        _("mot-de-passe/oublie/"),
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset_form.html",
            email_template_name="accounts/emails/password_reset_email.txt",
            subject_template_name="accounts/emails/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        _("mot-de-passe/oublie/envoye/"),
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        format_lazy("{}<uidb64>/<token>/", _("mot-de-passe/reinitialiser/")),
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        _("mot-de-passe/reinitialise/"),
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
