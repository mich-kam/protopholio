from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from .forms import ProfileForm, RegisterForm


def register(request):
    """Inscription puis connexion automatique."""
    if request.user.is_authenticated:
        return redirect("courses:dashboard")

    next_url = request.POST.get("next") or request.GET.get("next", "")
    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(
            request, _("Bienvenue %(username)s ! Votre compte a bien été créé.") % {"username": user.username}
        )

        is_safe = url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        )
        return redirect(next_url if is_safe else "courses:dashboard")

    return render(request, "accounts/register.html", {"form": form, "next": next_url})


@login_required
def profile(request):
    """Mon compte : informations personnelles."""
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Vos informations ont été mises à jour."))
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


class PasswordChangeViewFr(SuccessMessageMixin, PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")
    success_message = gettext_lazy("Votre mot de passe a été modifié.")
