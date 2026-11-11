from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Utilisateur personnalisé.

    Django recommande de définir son propre modèle utilisateur dès le début d'un
    projet : cela permet de l'enrichir plus tard (téléphone, avatar...) sans
    migration douloureuse. Ici, seule l'adresse e-mail devient obligatoire et unique.
    """

    email = models.EmailField("adresse e-mail", unique=True)

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"


class FailedLogin(models.Model):
    """
    Tentative de connexion échouée (base de la limitation anti brute-force, voir throttle.py).

    Stockée en base plutôt qu'en mémoire : plusieurs processus Gunicorn partagent ainsi le même compteur.
    """

    identifier = models.CharField("identifiant saisi", max_length=150, db_index=True)
    created_at = models.DateTimeField("date", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "tentative de connexion échouée"
        verbose_name_plural = "tentatives de connexion échouées"

    def __str__(self):
        return f"{self.identifier} — {self.created_at:%d/%m/%Y %H:%M}"
