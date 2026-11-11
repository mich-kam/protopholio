#!/usr/bin/env bash
# Script de build pour Render (arrêt immédiat à la première erreur).
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Optionnel : crée le super-utilisateur automatiquement (utile sans accès shell).
# Définissez DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL et DJANGO_SUPERUSER_PASSWORD.
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_EMAIL:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  python manage.py createsuperuser --no-input || echo "Super-utilisateur déjà existant : ignoré."
fi

# Optionnel : charge les données de démonstration (profil, projets, cours d'exemple).
# À activer pour le premier déploiement, puis à repasser à 0.
if [[ "${LOAD_DEMO_DATA:-0}" == "1" ]]; then
  python manage.py seed_demo
fi
