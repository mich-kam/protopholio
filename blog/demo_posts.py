"""
Articles d'exemple chargés par `python manage.py seed_demo`.

Ce sont des textes pédagogiques génériques, rédigés pour que le blog ne soit pas vide :
relisez-les, adaptez-les à votre voix (ou supprimez-les) avant de les publier pour de bon.
Contenu au format Markdown.
"""

# (titre, résumé, tags, jours d'ancienneté, à la une, contenu Markdown)
DEMO_POSTS = [
    (
        "5 réflexes pour des mots de passe vraiment solides",
        "Un mot de passe faible est la porte d'entrée préférée des pirates. Voici cinq habitudes simples pour protéger tous vos comptes.",
        "Cybersécurité, Bonnes pratiques",
        24,
        False,
        """Le mot de passe reste la première barrière entre un inconnu et vos comptes. Pourtant, **123456** et **motdepasse** figurent encore parmi les plus utilisés. Voici cinq réflexes à adopter dès aujourd'hui.

## 1. Privilégiez la longueur à la complexité

Un mot de passe de **14 caractères ou plus** est bien plus difficile à deviner qu'un mot court rempli de symboles. Une phrase de passe fonctionne très bien : quatre ou cinq mots sans rapport entre eux, par exemple `cheval-bleu-ordinateur-lundi`.

## 2. Un mot de passe différent pour chaque compte

Quand un site est piraté, les mots de passe volés sont testés partout ailleurs (messagerie, réseaux sociaux, banque). Réutiliser le même mot de passe, c'est donner la clé de toute sa vie numérique à celui qui en trouve une seule.

## 3. Utilisez un gestionnaire de mots de passe

Impossible de retenir des dizaines de mots de passe longs et uniques. Un **gestionnaire de mots de passe** les génère, les stocke chiffrés et les remplit pour vous. Vous n'avez plus qu'à retenir un seul mot de passe maître, très solide.

## 4. Activez la double authentification

La vérification en deux étapes (code reçu par application ou SMS, clé de sécurité) bloque l'accès même si votre mot de passe est volé. Activez-la au minimum sur votre messagerie, vos réseaux sociaux et vos services financiers.

## 5. Ne partagez jamais votre mot de passe

Aucun service sérieux ne vous le demandera par message, appel ou e-mail. Si quelqu'un le réclame, c'est une tentative d'arnaque.

> **À retenir :** longueur, unicité, gestionnaire, double authentification, discrétion. Cinq habitudes, dix minutes de mise en place, et vos comptes sont bien mieux protégés.
""",
    ),
    (
        "Phishing : comment reconnaître un message piégé",
        "Faux e-mails, faux SMS, faux messages WhatsApp : apprenez à repérer les signaux d'alerte et les bons réflexes avant de cliquer.",
        "Cybersécurité, Sensibilisation",
        15,
        True,
        """Le **phishing** (ou hameçonnage) consiste à se faire passer pour une entité de confiance (banque, opérateur, administration, réseau social) afin de vous pousser à donner un mot de passe, des coordonnées bancaires ou à installer un logiciel malveillant. C'est aujourd'hui l'une des portes d'entrée les plus courantes des attaques.

## Les signaux d'alerte

- **L'urgence ou la menace** : « votre compte sera bloqué dans 24 h », « action immédiate requise ».
- **L'expéditeur douteux** : l'adresse ressemble à la vraie mais contient une faute ou un domaine étrange.
- **Les liens trompeurs** : le texte affiché n'est pas la vraie destination. Survolez le lien sans cliquer pour voir l'adresse réelle.
- **Les pièces jointes inattendues** : facture, CV, « document important » que vous n'attendiez pas.
- **Les fautes et le ton étrange** : un message officiel est rarement mal écrit ou trop familier.
- **La demande d'informations sensibles** : un service sérieux ne vous demande jamais votre mot de passe ou votre code secret.

## Que faire face à un message suspect ?

1. **Ne cliquez sur rien** et n'ouvrez pas la pièce jointe.
2. **Vérifiez par un autre canal** : ouvrez vous-même le site officiel (en tapant l'adresse) ou appelez le service au numéro habituel.
3. **Signalez et supprimez** le message.
4. Si vous avez déjà cliqué ou saisi des informations : **changez immédiatement le mot de passe** concerné, activez la double authentification et prévenez votre banque si des données financières sont en jeu.

## Un réflexe simple

Avant de cliquer, posez-vous trois questions : *est-ce que j'attendais ce message ? L'expéditeur est-il vraiment celui qu'il prétend être ? Qu'est-ce qu'on me pousse à faire, et pourquoi si vite ?*

En cas de doute, ne cliquez pas : prenez une minute pour vérifier. Cette minute peut vous éviter des semaines de problèmes.
""",
    ),
    (
        "Sécuriser son réseau Wi-Fi à la maison ou au bureau",
        "Sept réglages simples pour empêcher les intrus de profiter de votre connexion, ou pire, d'espionner votre réseau.",
        "Cybersécurité, Réseaux",
        8,
        False,
        """Un réseau Wi-Fi mal protégé permet à n'importe qui à portée de signal de profiter de votre connexion, voire d'espionner ce qui y circule. Quelques réglages suffisent à fermer la porte.

## 1. Changez les identifiants de la box ou du routeur

Les mots de passe d'administration fournis par défaut (« admin / admin ») sont connus de tous. Dès l'installation, définissez un mot de passe d'administration **unique et long**.

## 2. Choisissez un chiffrement moderne

Dans les paramètres Wi-Fi, activez **WPA3** si votre matériel le propose, sinon **WPA2 (AES)**. N'utilisez jamais **WEP** ni un réseau « ouvert » sans mot de passe : ils sont trivialement contournables.

## 3. Utilisez un mot de passe Wi-Fi solide

Une phrase de passe d'au moins 16 caractères. Évitez le nom de la famille, de l'entreprise ou un numéro de téléphone.

## 4. Créez un réseau invité

Les visiteurs, les objets connectés (caméras, télévisions, ampoules) et vos appareils de travail ne devraient pas partager le même réseau. Le **réseau invité** isole ces usages : si un appareil est compromis, le reste est protégé.

## 5. Désactivez ce qui est inutile

- **WPS** (connexion par bouton ou code à 8 chiffres) : une faiblesse connue.
- **L'administration à distance** de la box, si vous ne vous en servez pas.

## 6. Mettez à jour le micrologiciel

Les fabricants corrigent régulièrement des failles. Vérifiez les mises à jour de votre routeur (ou activez les mises à jour automatiques) et remplacez le matériel qui n'est plus supporté.

## 7. Surveillez les appareils connectés

L'interface de la box affiche la liste des appareils connectés. Un appareil inconnu ? Changez le mot de passe Wi-Fi.

> **Au bureau**, ajoutez une règle d'or : un mot de passe Wi-Fi différent pour les employés et pour les invités, et un changement lorsqu'un collaborateur quitte l'entreprise.
""",
    ),
    (
        "Django : 7 réglages de sécurité à vérifier avant le déploiement",
        "Django est sûr par défaut sur beaucoup de points, mais la mise en production demande quelques réglages précis. Ma liste de contrôle.",
        "Django, Cybersécurité, Développement",
        3,
        False,
        """Un site Django est sûr par défaut sur beaucoup de points (protection CSRF, échappement des gabarits, hachage des mots de passe...). Mais la mise en production demande quelques réglages précis. Voici ma liste de contrôle.

## 1. `DEBUG = False`

Le mode debug affiche des détails sensibles (chemins, réglages, requêtes SQL) en cas d'erreur. **Jamais en production.**

## 2. Une `SECRET_KEY` secrète

Elle signe les sessions et les jetons. Lisez-la depuis une **variable d'environnement**, ne la versionnez jamais, et changez-la si elle a fuité.

## 3. `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS`

Listez uniquement vos vrais domaines. Cela bloque les attaques par en-tête `Host` falsifié.

## 4. HTTPS partout

```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

Derrière un proxy (Render, Heroku), ajoutez `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`.

## 5. Lancez le contrôle intégré

```
python manage.py check --deploy
```

Django analyse vos réglages et signale ce qui manque. C'est gratuit : utilisez-le avant chaque mise en ligne.

## 6. Protégez les fichiers privés

Les fichiers réservés (cours payants, documents) ne doivent pas être servis par une URL publique. Passez par une vue qui **vérifie les droits** avant d'envoyer le fichier.

## 7. Mettez à jour les dépendances

Surveillez les versions de Django et de vos bibliothèques : les correctifs de sécurité sont publiés régulièrement.

> Aucun de ces réglages n'est compliqué. C'est leur oubli qui coûte cher.
""",
    ),
]
