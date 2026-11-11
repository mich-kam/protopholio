from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from . import throttle


class EmailOrUsernameBackend(ModelBackend):
    """
    Authentifie avec le nom d'utilisateur OU l'adresse e-mail (insensible à la casse),
    avec limitation des tentatives (voir throttle.py).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if not username or password is None:
            return None

        if throttle.is_locked(username):
            # Django interrompt alors l'authentification pour ce jeu d'identifiants (ni indice, ni test du mot de passe).
            raise PermissionDenied("Trop de tentatives échouées.")

        candidates = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username))
        for user in candidates:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        if not candidates:
            # Même coût de calcul qu'un vrai test : empêche de deviner quels comptes existent.
            User().set_password(password)
        return None
