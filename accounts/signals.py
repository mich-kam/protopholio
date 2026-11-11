from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from . import throttle


@receiver(user_login_failed)
def remember_failed_login(sender, credentials, request=None, **kwargs):
    throttle.record_failure(credentials.get("username"))


@receiver(user_logged_in)
def forget_failed_logins(sender, user, request=None, **kwargs):
    # L'utilisateur a pu se connecter avec son nom d'utilisateur OU son e-mail : on efface les deux.
    throttle.clear(user.get_username(), user.email)
