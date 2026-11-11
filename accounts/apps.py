from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"
    verbose_name = "Comptes"

    def ready(self):
        from . import signals  # noqa: F401  (enregistre les récepteurs de signaux)
