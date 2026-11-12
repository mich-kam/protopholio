#!/usr/bin/env bash
# Script de build pour Render (arrêt immédiat à la première erreur).
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Crée le super-utilisateur, ou aligne son mot de passe sur la variable
# DJANGO_SUPERUSER_PASSWORD (createsuperuser ignore un compte déjà existant).
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ["DJANGO_SUPERUSER_USERNAME"]
email = os.environ.get("DJANGO_SUPERUSER_EMAIL") or "admin@example.com"
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
user = (
    User.objects.filter(username__iexact=username).first()
    or User.objects.filter(email__iexact=email).first()
    or User.objects.filter(is_superuser=True).order_by("id").first()
)
if user is None:
    user = User.objects.create_superuser(username, email, password)
else:
    # Le compte créé au premier déploiement n'a pas forcément le nom « admin ».
    if user.username.lower() != username.lower() and not User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
        user.username = username
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
# Un mauvais mot de passe répété bloque aussi l'administration pendant 15 minutes.
from accounts.models import FailedLogin
keys = {username.lower(), email.lower(), user.username.lower(), (user.email or "").lower()}
FailedLogin.objects.filter(identifier__in=keys).delete()
print("admin-ready", user.username)
PY
fi

# Optionnel : charge les données de démonstration (profil, projets, cours d'exemple).
# À activer pour le premier déploiement, puis à repasser à 0.
if [[ "${LOAD_DEMO_DATA:-0}" == "1" ]]; then
  python manage.py seed_demo
fi
