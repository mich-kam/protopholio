"""
Mesures de sécurité réellement appliquées par ce site (affichées sur la page /securite/).

Règle d'or : ne lister ici que ce qui est VRAI et vérifiable dans le code.
Si une mesure est retirée du projet, retirez-la aussi de cette liste.
"""

from django.utils.translation import gettext_lazy as _

# (icône, titre, description)
SECURITY_MEASURES = [
    (
        "lock",
        _("Connexion chiffrée (HTTPS)"),
        _(
            "En production, toutes les pages sont servies en HTTPS et le navigateur est invité à ne "
            "plus jamais utiliser HTTP (HSTS)."
        ),
    ),
    (
        "shield",
        _("Mots de passe hachés"),
        _(
            "Les mots de passe ne sont jamais stockés en clair : seul un hachage PBKDF2 salé est conservé, "
            "et les mots de passe trop faibles ou courants sont refusés."
        ),
    ),
    (
        "zap",
        _("Limitation des tentatives de connexion"),
        _(
            "Après plusieurs échecs, la connexion à un compte est temporairement bloquée : "
            "cela rend les attaques par force brute inefficaces."
        ),
    ),
    (
        "check-circle",
        _("Protection CSRF"),
        _("Chaque formulaire embarque un jeton unique qui empêche un site tiers d'agir à votre place."),
    ),
    (
        "user",
        _("Sessions protégées"),
        _(
            "Les cookies de session ne sont pas lisibles par JavaScript (HttpOnly), sont limités au même site "
            "(SameSite) et marqués « Secure » en production."
        ),
    ),
    (
        "book",
        _("Cours réservés aux acheteurs"),
        _(
            "Les fichiers de cours ne sont jamais accessibles par une URL publique : ils sont envoyés "
            "uniquement après vérification de l'achat."
        ),
    ),
    (
        "file-text",
        _("Reçus et commandes privés"),
        _(
            "Un reçu n'est consultable que par son propriétaire. "
            "Pour tout autre visiteur, il n'existe tout simplement pas."
        ),
    ),
    (
        "mail",
        _("Anti-spam sans espionnage"),
        _("Le formulaire de contact utilise un piège invisible (honeypot) plutôt qu'un traceur publicitaire."),
    ),
    (
        "database",
        _("Aucune donnée bancaire"),
        _("Ce site ne collecte ni ne stocke aucun numéro de carte bancaire."),
    ),
    (
        "eye-off",
        _("Pages privées non indexées"),
        _("Votre espace, vos commandes et vos reçus sont exclus des moteurs de recherche."),
    ),
    (
        "terminal",
        _("En-têtes de sécurité"),
        _(
            "Protection contre le détournement de clic, l'interprétation erronée de fichiers, les fuites de "
            "référent et l'accès non sollicité à la caméra, au micro ou à la position."
        ),
    ),
    (
        "code",
        _("Entrées nettoyées"),
        _(
            "Les contenus saisis sont échappés à l'affichage et le contenu des articles est filtré "
            "pour bloquer tout code malveillant."
        ),
    ),
]
