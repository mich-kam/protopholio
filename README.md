# Portfolio + plateforme de cours en ligne (Django)

Portfolio personnel (services, parcours, projets, contact) couplé à une boutique de cours :
inscription / connexion, achat (paiement **simulé**), espace « Mes cours », reçus imprimables et téléchargement protégé.

**Stack :** Django 6.1 · Tailwind CSS 4 (CDN) · WhiteNoise · Gunicorn · PostgreSQL (SQLite en local).

## Fonctionnalités

**Site vitrine**
- Accueil animé : hero avec **rôles en machine à écrire**, aurore colorée, carte de code personnalisée (bordure dégradée, inclinaison 3D au survol), statistiques *réelles* (jamais inventées), bandeau de technologies.
- Sections **Services**, **Cybersécurité** (thème sombre « terminal », masquée s'il n'y a aucune compétence de cette catégorie), **À propos** (compétences, parcours), **Portfolio**, **Méthode de travail**, **Cours**, **Témoignages** (visible seulement s'il y en a), **FAQ**, **Contact**.
- **Palette de commandes** (`Ctrl+K` ou `/`) : navigation instantanée vers une section, une page ou une action (thème, WhatsApp, e-mail…).
- **Portrait** en page d'accueil (hero et « À propos »), **radar des compétences** par domaine (SVG), réseau animé dans la section cybersécurité.
- Image d'aperçu de partage (WhatsApp, Facebook, LinkedIn) générée avec ta photo : `python manage.py make_social_card`.
- Mode clair / sombre mémorisé, menu mobile, navigation qui suit le scroll, halo lumineux sur les cartes, barre de progression, retour en haut.
- Tous les effets respectent le réglage système « réduire les animations ».
- Bouton **WhatsApp** flottant (si un numéro est renseigné), badge « Disponible pour de nouvelles missions ».
- Formulaire de contact avec anti-spam (honeypot) et notification e-mail.

**CV en ligne** (`/cv/`)
- Généré automatiquement depuis les données du site (profil, compétences dont **cybersécurité**, parcours, projets) : toujours à jour.
- Photo incluse, **une page A4**, bouton « Télécharger en PDF » (impression du navigateur). Aucune donnée sensible (passeport, date de naissance, adresse).
- Un PDF prêt à envoyer est fourni : `CV_Michel_Kamango_Lodi.pdf` (à régénérer après modification du contenu, voir plus bas).

**Blog** (`/blog/`)
- Articles en **Markdown** (nettoyé contre tout code malveillant), tags, recherche, pagination, article « à la une », temps de lecture.
- Publication programmable (date future), aperçu des brouillons pour l'administrateur, **flux RSS** (`/blog/rss.xml`), données structurées `BlogPosting`.
- 4 articles d'exemple sur la cybersécurité et Django (`seed_demo`) : à relire avant publication.

**Sécurité du site** (`/securite/`)
- Page listant les mesures **réellement** appliquées (HTTPS/HSTS, mots de passe hachés, anti brute-force, CSRF, cours privés...) et `security.txt` (RFC 9116) pour la divulgation responsable.
- **Limitation des tentatives de connexion** : 5 échecs en 15 min bloquent le compte temporairement (y compris l'administration).
- En-tête `Permissions-Policy`, journal des échecs de connexion en lecture seule dans l'admin.

**Boutique de cours**
- Catalogue avec **recherche, filtres (niveau, prix), tri et pagination**.
- **Avis et notes** réservés aux acheteurs (une note de 1 à 5 et un commentaire, modifiables), moyenne affichée sur les cartes, modération depuis l'admin.
- Page cours : objectifs, prérequis, durée, cours similaires, partage (WhatsApp, Facebook, copie du lien).
- Commande en étapes, paiement simulé, **e-mail de confirmation**, **reçu imprimable / PDF**.
- Tableau de bord : cours achetés, total investi, historique des commandes, recommandations.
- Fichiers de cours privés, téléchargeables uniquement par les acheteurs.

**Comptes**
- Inscription, connexion par **nom d'utilisateur ou e-mail**, déconnexion.
- **Mot de passe oublié** (lien par e-mail), changement de mot de passe, page « Mon compte ».

**Professionnel / SEO**
- Balises Open Graph (aperçu riche sur WhatsApp, Facebook, LinkedIn), URL canoniques, données structurées JSON-LD
  (`Person`, `Course`), `sitemap.xml`, `robots.txt`, pages privées en `noindex`.
- Route `/healthz/` (contrôle de santé avec test de la base), pages 404/500 soignées.
- Administration française : export CSV des commandes (protégé contre l'injection de formules), nombre de ventes par cours,
  validation manuelle des paiements.

## Structure

```
.
├── manage.py
├── requirements.txt          # dépendances épinglées
├── Procfile                  # Heroku (+ Railway pour le process web)
├── build.sh                  # script de build Render
├── render.yaml               # Blueprint Render (web + PostgreSQL)
├── .python-version           # Python 3.12
├── .env.example              # variables d'environnement documentées
├── config/                   # settings.py, urls.py, wsgi.py, asgi.py
├── accounts/                 # User personnalisé, connexion e-mail, profil, mot de passe oublié, anti brute-force
├── portfolio/                # Profile, Service, Skill, TimelineItem, Project, Testimonial, FAQ, ContactMessage
│   ├── templatetags/ui.py    #   {% icon %} (SVG inline), étoiles, filtre code_lines
│   ├── radar.py, seo.py      #   radar des compétences (SVG) et JSON-LD
│   ├── security_info.py      #   mesures de sécurité affichées sur /securite/
│   ├── sitemaps.py
│   └── management/commands/  #   seed_demo, make_social_card
├── courses/                  # Course, Order, Review, paiement simulé, e-mails, reçus, tableau de bord
├── blog/                     # Post (Markdown nettoyé), flux RSS, articles d'exemple
├── templates/                # base.html, partials/, portfolio/, courses/, blog/, accounts/, 404, 500
└── static/                   # css/site.css, js/main.js, img/profile.jpg, img/social-card.jpg
```

## Lancer en local (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy .env.example .env        # puis éditez SECRET_KEY (DEBUG=True est déjà prévu)

python manage.py migrate
python manage.py seed_demo    # optionnel : profil, services, FAQ, projets et cours d'exemple
python manage.py createsuperuser
python manage.py runserver 8321
```

- Site : http://127.0.0.1:8321/ — Administration : http://127.0.0.1:8321/admin/
- Tests : `python manage.py test`
- En local, les e-mails (confirmation d'achat, mot de passe oublié) s'affichent dans la console du serveur.

## Personnaliser le contenu (depuis /admin/)

| Je veux modifier… | Section de l'admin |
|---|---|
| Mon nom, photo, accroche, **rôles animés du hero**, coordonnées, WhatsApp, réseaux sociaux, disponibilité | **Profil** |
| Les prestations affichées en page d'accueil | **Services** |
| Mes compétences (la catégorie « Cybersécurité » alimente la section dédiée), expériences, formations, certifications | **Compétences** / **Parcours** |
| Mes projets (capture, lien GitHub, démo) | **Projets** |
| Mes articles (Markdown, tags, publication programmée) | **Articles** |
| Les avis des apprenants (masquer un avis inapproprié) | **Avis** |
| Le journal des tentatives de connexion échouées | **Tentatives de connexion échouées** |
| Les avis clients (la section apparaît dès qu'il y en a un) | **Témoignages** |
| Les questions fréquentes | **Questions fréquentes** |
| Les cours (prix, objectifs, fichier ou lien, mise en avant) | **Cours** |
| Les commandes, validation manuelle, export Excel | **Commandes** |

## Variables d'environnement

| Variable | Rôle | Défaut |
|---|---|---|
| `SECRET_KEY` | Clé secrète Django. **Obligatoire** si `DEBUG=False`. | — |
| `DEBUG` | Mode debug. | `False` |
| `ALLOWED_HOSTS` | Domaines autorisés (virgules). Render/Railway ajoutent le leur. | vide |
| `CSRF_TRUSTED_ORIGINS` | Origines `https://...` autorisées pour les POST. | vide |
| `DATABASE_URL` | URL PostgreSQL. Absente = SQLite. | SQLite |
| `DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD` | Création auto du super-utilisateur (`build.sh`). | — |
| `LOAD_DEMO_DATA` | `1` = exécute `seed_demo` au build (1er déploiement seulement). | `0` |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | Serveur SMTP. **Nécessaire en production** pour les e-mails clients. | logs console |
| `CONTACT_RECIPIENT` | Adresse qui reçoit les messages du formulaire de contact. | — |
| `CURRENCY_SYMBOL`, `CURRENCY_CODE` | Monnaie affichée (`$`) et code ISO pour le SEO (`USD`). | `$` / `USD` |
| `MEDIA_ROOT` | Dossier des fichiers envoyés (disque persistant). | `./media` |

## Déploiement

### Render (le plus simple : Blueprint)
1. Poussez le projet sur GitHub.
2. Render → **New → Blueprint** → choisissez le dépôt. `render.yaml` crée le service web et la base PostgreSQL.
3. Renseignez `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` quand Render les demande.
4. 1er déploiement : passez `LOAD_DEMO_DATA` à `1`, puis remettez `0` (sinon les éléments d'exemple supprimés seraient recréés).
5. Ajoutez les variables `EMAIL_*` pour que les e-mails de confirmation et de mot de passe oublié soient réellement envoyés.

### Railway
1. New Project → Deploy from GitHub, puis ajoutez le plugin **PostgreSQL**.
2. Variables : `SECRET_KEY`, `DEBUG=False`, `DATABASE_URL=${{Postgres.DATABASE_URL}}`.
3. Build command : `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. Pre-deploy command : `python manage.py migrate --noinput` (le `Procfile` fournit le process `web` avec Gunicorn).
5. Créez le super-utilisateur : `railway run python manage.py createsuperuser`.

### Heroku
```bash
heroku create nom-de-l-app
heroku addons:create heroku-postgresql
heroku config:set SECRET_KEY="..." DEBUG=False ALLOWED_HOSTS=nom-de-l-app.herokuapp.com
git push heroku main          # collectstatic auto, `release:` du Procfile lance migrate
heroku run python manage.py createsuperuser
```
Définissez `SECRET_KEY` **avant** le premier `git push` : le build refuse de démarrer sans elle.

## Photo, CV et image de partage

- **Photo** : `static/img/profile.jpg` est livrée avec le site (elle survit aux redéploiements). Une photo envoyée via l'admin (**Profil**) a priorité.
- **Image de partage** : après un changement de nom, de titre, de rôles ou de photo, relancez `python manage.py make_social_card`.
- **CV PDF** : ouvrez `/cv/` puis « Télécharger en PDF » (ou, avec Edge/Chrome en ligne de commande :
  `msedge --headless=new --no-pdf-header-footer --print-to-pdf=CV.pdf http://127.0.0.1:8321/cv/`).

## Points d'attention

- **Médias non persistants.** Le disque de Render/Heroku/Railway est éphémère : photos de projets, images de cours
  et fichiers de cours envoyés par l'admin sont perdus à chaque redéploiement. Utilisez un disque persistant
  (`MEDIA_ROOT`) ou un stockage objet (S3, Cloudinary via `django-storages`) pour la vraie production.
- **Fichiers de cours privés.** Ils sont stockés dans `media/courses/files/` et ne sont **jamais** servis par
  `/media/`. Seule la vue `courses:download` les envoie, aux acheteurs uniquement.
- **Paiement simulé.** `courses/payments.py::charge()` renvoie toujours `True`. Pour un vrai paiement
  (Stripe, PayPal, Mobile Money), remplacez ce corps de fonction puis passez `SIMULATED = False` :
  les bandeaux « mode démonstration » disparaissent du site et des reçus. Vous pouvez aussi valider une commande
  à la main dans l'admin (action « Marquer comme payées »).
- **E-mails.** Sans `EMAIL_HOST`, les e-mails sont seulement écrits dans les logs : le « mot de passe oublié »
  ne fonctionnera pour vos visiteurs qu'une fois un SMTP configuré.
- **Tailwind via CDN.** Pratique (aucun build) mais compilé dans le navigateur. Pour un fort trafic,
  passez à une version compilée.
- **CV public.** Si vous envoyez un CV via l'admin, il sera téléchargeable par tous : retirez-en passeport,
  date de naissance et adresse exacte.
