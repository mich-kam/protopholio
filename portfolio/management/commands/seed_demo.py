"""
Charge un jeu de données initial (profil, compétences, parcours, projets, cours d'exemple).

    python manage.py seed_demo

La commande est IDEMPOTENTE : elle ne remplace jamais ce qui existe déjà
(relancez-la sans risque). Tout reste modifiable depuis /admin/.
"""

from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.demo_posts import DEMO_POSTS
from blog.models import Post
from courses.models import Course
from portfolio.demo_i18n import (
    COURSES_EN,
    FAQS_EN,
    POSTS_EN,
    PROFILE_EN,
    PROJECTS_EN,
    SERVICES_EN,
    SKILLS_EN,
    TIMELINE_EN,
    fill_en,
)
from portfolio.models import FAQ, GalleryPhoto, Profile, Project, ProjectImage, Service, Skill, TimelineItem

DEMO_IMG = Path(settings.BASE_DIR) / "static" / "img" / "demo"

# Image principale par titre de projet (fichiers dans static/img/demo/).
PROJECT_DEMO_IMAGES = {
    "Application de gestion scolaire": "project-school.jpg",
    "Application de gestion de restaurant": "project-restaurant.jpg",
    "Réseau local d'entreprise": "project-network.jpg",
    "Portfolio & plateforme de cours en ligne": "project-portfolio.jpg",
    "Mes Liens — page de liens personnelle": "project-links.jpg",
}

# Couvertures cours / blog (même dossier demo).
COURSE_DEMO_IMAGES = {
    "Python pour débutants": "course-python.jpg",
    "HTML, CSS et JavaScript : créer son premier site": "course-web.jpg",
    "Bases de données avec MySQL et SQL": "course-sql.jpg",
    "Cybersécurité : les bases pour se protéger": "course-security.jpg",
}

BLOG_DEMO_IMAGES = {
    "5 réflexes pour des mots de passe vraiment solides": "blog-passwords.jpg",
    "Phishing : comment reconnaître un message piégé": "blog-phishing.jpg",
    "Sécuriser son réseau Wi-Fi à la maison ou au bureau": "blog-wifi.jpg",
    "Django : 7 réglages de sécurité à vérifier avant le déploiement": "blog-django.jpg",
}

# Galerie photos d'exemple : (titre, fichier, type, légende_fr, légende_en, titre_en)
GALLERY_DEMO = [
    (
        "Espace de travail",
        "gallery-workspace.jpg",
        GalleryPhoto.Kind.WORK,
        "Bureau de développement — environnement de travail quotidien.",
        "Workspace",
        "Developer desk — everyday working environment.",
    ),
    (
        "Infrastructure réseau",
        "gallery-network.jpg",
        GalleryPhoto.Kind.WORK,
        "Baie de brassage et câblage réseau en situation réelle.",
        "Network infrastructure",
        "Server rack and structured cabling on site.",
    ),
    (
        "Session de formation",
        "gallery-training.jpg",
        GalleryPhoto.Kind.EVENT,
        "Atelier pratique — apprentissage du développement web.",
        "Training session",
        "Hands-on workshop — learning web development.",
    ),
    (
        "Focus code",
        "gallery-coding.jpg",
        GalleryPhoto.Kind.OTHER,
        "Concentration sur un projet en cours de réalisation.",
        "Coding focus",
        "Focused work on a project in progress.",
    ),
]


def _attach_demo_image(field, filename, save_name=None):
    """Copie une image depuis static/img/demo/ vers un ImageField (vide ou fichier média perdu)."""
    path = DEMO_IMG / filename
    if not path.exists():
        return False
    if field.name:
        try:
            if field.storage.exists(field.name):
                return False
        except Exception:
            pass
    with path.open("rb") as fh:
        field.save(save_name or filename, File(fh), save=True)
    return True

S = Skill.Category
K = TimelineItem.Kind
I = Service.Icon  # noqa: E741

PROFILE = {
    "full_name": "Kamango Lodi Michel",
    "headline": "Développeur web, bases de données & cybersécurité",
    "roles": "Développeur web, Spécialiste cybersécurité, Réseaux & vidéosurveillance, Formateur en ligne",
    "tagline": (
        "Licencié en Sciences Informatiques, je conçois des applications web avec Python, PHP "
        "et JavaScript, je sécurise réseaux et systèmes, et je partage mes connaissances "
        "à travers des cours en ligne."
    ),
    "about": (
        "Diplômé d'une Licence en Sciences Informatiques, j'ai suivi une formation en "
        "développement informatique, bases de données, traitement des données, support "
        "informatique, vidéosurveillance (CCTV) et réseaux.\n\n"
        "Je possède des connaissances pratiques en Python, PHP, JavaScript, HTML5, CSS3, MySQL "
        "et SQL, acquises à travers des stages et des projets académiques. Mon parcours m'a "
        "permis de développer des compétences en développement d'applications web, gestion des "
        "bases de données, analyse de données, résolution de problèmes techniques et support "
        "aux utilisateurs.\n\n"
        "Passionné par la cybersécurité, je m'intéresse à la protection des réseaux, des "
        "applications web et des données, ainsi qu'à la sensibilisation des utilisateurs aux "
        "bons réflexes.\n\n"
        "Curieux, rigoureux et à l'aise avec l'apprentissage rapide, j'aime travailler en équipe "
        "et sous pression pour livrer des solutions fiables."
    ),
    "email": "michk2216@gmail.com",
    "phone": "+243 810 081 623",
    # Même numéro que le téléphone : à vérifier (ou vider) dans l'admin si ce n'est pas un numéro WhatsApp.
    "whatsapp": "+243810081623",
    "location": "Kinshasa, RDC",
    "languages": "Français (C2) · Swahili (natif) · Lingala (C1) · Anglais (B2)",
    "available_for_work": True,
}

SERVICES = [
    (
        I.CODE,
        "Développement web & applications",
        "Conception d'applications web sur mesure avec Python, PHP, JavaScript, HTML5 et CSS3 : "
        "gestion de clients, de commandes, d'élèves ou de stocks.",
    ),
    (
        I.DATABASE,
        "Bases de données & analyse de données",
        "Modélisation et administration de bases MySQL / SQL, gestion des données applicatives, "
        "traitement et premières analyses de données.",
    ),
    (
        I.NETWORK,
        "Réseaux informatiques",
        "Installation et configuration de réseaux locaux (LAN) : câblage, routeurs, switches, "
        "adressage IP, partage de ressources et maintenance.",
    ),
    (
        I.CAMERA,
        "Vidéosurveillance (CCTV)",
        "Installation de caméras IP et analogiques (Hikvision), configuration de DVR / NVR, "
        "raccordement, mise en service et diagnostic des pannes.",
    ),
    (
        I.SHIELD,
        "Cybersécurité",
        "Sécurisation de vos réseaux, de vos applications web et de vos données : bonnes pratiques, "
        "durcissement des configurations et sensibilisation des utilisateurs.",
    ),
    (
        I.TOOL,
        "Support & maintenance informatique",
        "Dépannage des postes et des systèmes, maintenance des équipements, assistance aux "
        "utilisateurs et résolution rapide des incidents.",
    ),
    (
        I.BOOK,
        "Formation en ligne",
        "Des cours pratiques en programmation et bases de données, à suivre à votre rythme "
        "depuis votre espace personnel.",
    ),
]

FAQS = [
    (
        "Comment accéder à un cours après l'avoir acheté ?",
        "Dès que votre commande est validée, le cours apparaît dans votre espace « Mes cours ». "
        "Il vous suffit de vous connecter pour l'ouvrir ou le télécharger, quand vous le souhaitez.",
    ),
    (
        "Puis-je suivre un cours sur mon téléphone ?",
        "Oui. Le site est conçu pour s'adapter aux téléphones, tablettes et ordinateurs. "
        "Les fichiers téléchargeables dépendent du cours : la page de chaque cours précise ce qui est inclus.",
    ),
    (
        "Comment obtenir un reçu pour mon achat ?",
        "Un reçu est disponible pour chaque commande dans « Mes cours ». Vous pouvez l'imprimer "
        "ou l'enregistrer en PDF depuis votre navigateur. Une confirmation est aussi envoyée par e-mail.",
    ),
    (
        "J'ai oublié mon mot de passe, que faire ?",
        "Sur la page de connexion, cliquez sur « Mot de passe oublié ? », saisissez votre adresse e-mail "
        "et suivez le lien reçu pour en choisir un nouveau.",
    ),
    (
        "Comment vous contacter pour une mission ou un devis ?",
        "Utilisez le formulaire de contact en bas de page, écrivez-moi par e-mail ou contactez-moi "
        "directement par téléphone. Je réponds généralement rapidement.",
    ),
]

SKILLS = [
    # (nom, catégorie, niveau %) — niveaux indicatifs, à ajuster dans l'admin
    ("Python", S.LANGUAGES, 75),
    ("PHP", S.LANGUAGES, 70),
    ("JavaScript", S.LANGUAGES, 70),
    ("HTML5", S.WEB, 85),
    ("CSS3", S.WEB, 80),
    ("Développement d'applications web", S.WEB, 70),
    ("MySQL", S.DATA, 65),
    ("SQL", S.DATA, 65),
    ("Data Analytics", S.DATA, 55),
    ("Réseaux LAN, routeurs et switches", S.SYSTEMS, 70),
    ("Vidéosurveillance IP (Hikvision, DVR/NVR)", S.SYSTEMS, 75),
    ("Support et maintenance informatique", S.SYSTEMS, 80),
    # Niveaux indicatifs à ajuster dans l'admin (Compétences).
    ("Sécurité des réseaux", S.SECURITY, 65),
    ("Sécurité des applications web", S.SECURITY, 60),
    ("Protection des données", S.SECURITY, 60),
    ("Sensibilisation & bonnes pratiques", S.SECURITY, 70),
    ("Tests et vérification d'applications", S.TOOLS, 65),
    ("Résolution de problèmes", S.TOOLS, 80),
]

TIMELINE = [
    (
        K.EXPERIENCE,
        "Stagiaire en réseau informatique et vidéosurveillance",
        "AVOLIK – COTEBU / Friend's Building",
        "2024 – 2026",
        "Installation de caméras IP Hikvision, tirage et raccordement des câbles, configuration "
        "réseau et mise en service du système de vidéosurveillance (entrée, parking, salle informatique).",
    ),
    (
        K.EXPERIENCE,
        "Stagiaire en informatique",
        "Global Technology",
        "2024",
        "Support informatique, maintenance des équipements, assistance aux utilisateurs, "
        "configuration et dépannage des systèmes et réseaux.",
    ),
    (
        K.EDUCATION,
        "Licence LMD en Informatique",
        "Hope Africa University of Burundi — Bujumbura",
        "2026",
        "",
    ),
    (
        K.EDUCATION,
        "Diplôme d'État en Commercial et gestion",
        "Institut de l'Enano — Kindu, RDC",
        "2022",
        "",
    ),
    (
        K.CERTIFICATION,
        "Programmation Web : HTML5, CSS3, JavaScript, PHP, MySQL et Python",
        "FFBF Center, Bujumbura",
        "2023",
        "",
    ),
    (
        K.CERTIFICATION,
        "Réseaux informatiques",
        "AVOLIK Bujumbura",
        "2025",
        "Réseaux LAN, câblage, configuration des routeurs et switches, adressage IP, maintenance réseau.",
    ),
    (
        K.CERTIFICATION,
        "Installation de vidéosurveillance",
        "Global Technologies of Burundi",
        "2024",
        "Caméras IP et analogiques, DVR/NVR, câblage, maintenance CCTV, diagnostic des pannes.",
    ),
    (
        K.CERTIFICATION,
        "Électricité de base",
        "Global Technology Bujumbura",
        "2024",
        "",
    ),
    (
        K.CERTIFICATION,
        "Anglais",
        "FFBF Center, Bujumbura",
        "2023",
        "",
    ),
]

PROJECTS = [
    {
        "title": "Application de gestion scolaire",
        "description": (
            "Application web pour gérer élèves, cours, enseignants et résultats scolaires. "
            "Projet académique réalisé à Hope Africa University : modélisation des données, "
            "interfaces de saisie et consultation des notes."
        ),
        "technologies": "PHP, MySQL, HTML5, CSS3, JavaScript",
        "featured": True,
        "github_url": "",
        "demo_url": "",
    },
    {
        "title": "Application de gestion de restaurant",
        "description": (
            "Application web de gestion des clients et des commandes d'un restaurant "
            "(prise de commande, suivi, interface simple). Code source public sur GitHub."
        ),
        "technologies": "HTML5, CSS3, JavaScript, PHP, MySQL",
        "featured": True,
        "github_url": "https://github.com/mich-kam/restaurant-mich",
        "demo_url": "",
    },
    {
        "title": "Réseau local d'entreprise",
        "description": (
            "Installation et configuration d'un réseau LAN avec câblage structuré, "
            "routeurs/switches, adressage IP, partage de ressources et maintenance. "
            "Réalisé en stage chez AVOLIK (vidéosurveillance IP & réseau)."
        ),
        "technologies": "LAN, Câblage, Routeurs, Switches, Hikvision",
        "featured": False,
        "github_url": "",
        "demo_url": "",
    },
    {
        "title": "Portfolio & plateforme de cours en ligne",
        "description": (
            "Le site que vous visitez : portfolio bilingue FR/EN, blog, CV en ligne et "
            "boutique de cours (auth, commandes, paiement Flutterwave, espace apprenant, admin). "
            "Déployé sur Render avec PostgreSQL."
        ),
        "technologies": "Python, Django, Tailwind CSS, PostgreSQL, Gunicorn",
        "featured": False,
        "github_url": "https://github.com/mich-kam/protopholio",
        "demo_url": "https://ir-kamango-mich.onrender.com/",
    },
    {
        "title": "Mes Liens — page de liens personnelle",
        "description": (
            "Mini-site pour regrouper et partager des liens utiles (profil, projets, contact). "
            "Projet léger, déployable rapidement. Code sur GitHub."
        ),
        "technologies": "HTML, CSS, Python, Django",
        "featured": False,
        "github_url": "https://github.com/mich-kam/mesliens_project",
        "demo_url": "https://mesliens-project.onrender.com",
    },
]

COURSES = [
    {
        "title": "Python pour débutants",
        "short_description": "Apprenez les bases de Python pas à pas, avec des exercices pratiques.",
        "description": (
            "Un cours complet pour démarrer en programmation avec Python.\n\n"
            "Au programme : variables, conditions, boucles, fonctions, listes et dictionnaires, "
            "lecture et écriture de fichiers, et un mini-projet final."
        ),
        "level": Course.Level.BEGINNER,
        "price": Decimal("15.00"),
        "duration": "6 h de contenu · 12 leçons",
        "is_featured": True,
        "learning_outcomes": (
            "Comprendre les variables, les types et les opérateurs\n"
            "Écrire des conditions et des boucles\n"
            "Créer et réutiliser des fonctions\n"
            "Manipuler listes, dictionnaires et fichiers\n"
            "Réaliser un mini-projet complet"
        ),
        "requirements": "Aucun prérequis : il suffit d'un ordinateur et de curiosité.",
    },
    {
        "title": "HTML, CSS et JavaScript : créer son premier site",
        "short_description": "Les fondamentaux du web pour construire un site moderne et responsive.",
        "description": (
            "Découvrez comment fonctionne le web et créez votre premier site de A à Z.\n\n"
            "Structure HTML5, mise en forme CSS3, mise en page responsive et interactivité "
            "avec JavaScript."
        ),
        "level": Course.Level.BEGINNER,
        "price": Decimal("0.00"),
        "duration": "4 h de contenu · 8 leçons",
        "learning_outcomes": (
            "Structurer une page avec HTML5\n"
            "Mettre en forme avec CSS3\n"
            "Rendre un site responsive\n"
            "Ajouter de l'interactivité avec JavaScript"
        ),
        "requirements": "Savoir utiliser un ordinateur et un navigateur web.",
    },
    {
        "title": "Bases de données avec MySQL et SQL",
        "short_description": "Modéliser, interroger et administrer une base de données relationnelle.",
        "description": (
            "Apprenez à concevoir des bases de données fiables.\n\n"
            "Modélisation, requêtes SELECT / INSERT / UPDATE / DELETE, jointures, "
            "agrégations et bonnes pratiques."
        ),
        "level": Course.Level.INTERMEDIATE,
        "price": Decimal("20.00"),
        "duration": "5 h de contenu · 10 leçons",
        "learning_outcomes": (
            "Modéliser une base de données relationnelle\n"
            "Écrire des requêtes SELECT, INSERT, UPDATE et DELETE\n"
            "Maîtriser les jointures et les agrégations\n"
            "Appliquer les bonnes pratiques de conception"
        ),
        "requirements": "Notions de base en informatique.",
    },
    {
        "title": "Cybersécurité : les bases pour se protéger",
        "short_description": "Comprendre les menaces courantes et adopter les bons réflexes au quotidien.",
        "description": (
            "Une initiation accessible à la cybersécurité, pour les particuliers comme pour les petites structures.\n\n"
            "Phishing, mots de passe, réseaux Wi-Fi, sauvegardes : vous apprendrez à reconnaître les risques "
            "les plus fréquents et à vous en protéger concrètement."
        ),
        "level": Course.Level.BEGINNER,
        "price": Decimal("12.00"),
        "duration": "3 h de contenu · 6 leçons",
        "learning_outcomes": (
            "Comprendre les principales menaces (phishing, logiciels malveillants)\n"
            "Créer et gérer des mots de passe solides\n"
            "Sécuriser son réseau Wi-Fi et ses appareils\n"
            "Reconnaître et éviter les arnaques en ligne\n"
            "Mettre en place des sauvegardes fiables"
        ),
        "requirements": "Aucun prérequis technique.",
    },
]


class Command(BaseCommand):
    help = "Charge le profil, les projets et des cours d'exemple (idempotent)."

    def handle(self, *args, **options):
        translated = 0

        if Profile.objects.exists():
            self.stdout.write("Profil : déjà présent, conservé.")
            profile = Profile.objects.first()
        else:
            profile = Profile.objects.create(**PROFILE)
            self.stdout.write(self.style.SUCCESS("Profil créé."))
        if fill_en(profile, PROFILE_EN):
            profile.save(update_fields=[f"{k}_en" for k in PROFILE_EN])
            translated += 1

        created = 0
        for order, (icon, title, description) in enumerate(SERVICES):
            obj, was_created = Service.objects.get_or_create(
                title=title, defaults={"icon": icon, "description": description, "order": order}
            )
            created += was_created
            en = SERVICES_EN.get(title)
            if en and fill_en(obj, {"title": en[0], "description": en[1]}):
                obj.save(update_fields=["title_en", "description_en"])
                translated += 1
        self.stdout.write(f"Services : {created} créé(s).")

        created = 0
        for order, (question, answer) in enumerate(FAQS):
            obj, was_created = FAQ.objects.get_or_create(
                question=question, defaults={"answer": answer, "order": order}
            )
            created += was_created
            en = FAQS_EN.get(question)
            if en and fill_en(obj, {"question": en[0], "answer": en[1]}):
                obj.save(update_fields=["question_en", "answer_en"])
                translated += 1
        self.stdout.write(f"FAQ : {created} créée(s).")

        # Ancien libellé trop « junior » pour un site public.
        Skill.objects.filter(name="Data Analytics (niveau junior)").update(name="Data Analytics")

        created = 0
        for order, (name, category, level) in enumerate(SKILLS):
            obj, was_created = Skill.objects.get_or_create(
                name=name, defaults={"category": category, "level": level, "order": order}
            )
            created += was_created
            en_name = SKILLS_EN.get(name)
            if en_name and fill_en(obj, {"name": en_name}):
                obj.save(update_fields=["name_en"])
                translated += 1
        self.stdout.write(f"Compétences : {created} créée(s).")

        created = 0
        for order, (kind, title, organization, period, description) in enumerate(TIMELINE):
            obj, was_created = TimelineItem.objects.get_or_create(
                kind=kind,
                title=title,
                defaults={
                    "organization": organization,
                    "period": period,
                    "description": description,
                    "order": order,
                },
            )
            created += was_created
            en = TIMELINE_EN.get((kind, title))
            if en and fill_en(obj, {"title": en[0], "organization": en[1], "description": en[2]}):
                obj.save(update_fields=["title_en", "organization_en", "description_en"])
                translated += 1
        self.stdout.write(f"Parcours : {created} élément(s) créé(s).")

        created = 0
        photos = 0
        for order, data in enumerate(PROJECTS):
            obj, was_created = Project.objects.get_or_create(
                title=data["title"], defaults={**data, "order": order}
            )
            created += was_created
            # Rafraîchit les textes / liens publics (sans écraser une image déjà uploadée).
            changed = []
            for field in ("description", "technologies", "github_url", "demo_url", "featured"):
                value = data.get(field, getattr(obj, field))
                if getattr(obj, field) != value:
                    setattr(obj, field, value)
                    changed.append(field)
            if obj.order != order:
                obj.order = order
                changed.append("order")
            if changed:
                obj.save(update_fields=changed)
            en = PROJECTS_EN.get(data["title"])
            if en and fill_en(obj, en):
                obj.save(update_fields=["title_en", "description_en", "technologies_en"])
                translated += 1
            demo_file = PROJECT_DEMO_IMAGES.get(data["title"])
            if demo_file and _attach_demo_image(obj.screenshot, demo_file):
                photos += 1
            # Une capture secondaire pour le projet mis en avant
            if data.get("featured") and demo_file and obj.images.count() == 0:
                extra = DEMO_IMG / demo_file
                if extra.exists():
                    img = ProjectImage(project=obj, caption="Aperçu de l'interface", order=0)
                    with extra.open("rb") as fh:
                        img.image.save(f"extra-{demo_file}", File(fh), save=True)
                    img.caption_en = "Interface preview"
                    img.save(update_fields=["caption_en"])
                    photos += 1
        self.stdout.write(f"Projets : {created} créé(s), {photos} image(s) ajoutée(s).")

        created = 0
        for order, (title, filename, kind, caption, title_en, caption_en) in enumerate(GALLERY_DEMO):
            obj, was_created = GalleryPhoto.objects.get_or_create(
                title=title,
                defaults={
                    "caption": caption,
                    "kind": kind,
                    "order": order,
                    "is_published": True,
                },
            )
            created += was_created
            if fill_en(obj, {"title": title_en, "caption": caption_en}):
                obj.save(update_fields=["title_en", "caption_en"])
                translated += 1
            if _attach_demo_image(obj.image, filename):
                pass
        self.stdout.write(f"Galerie photos : {created} photo(s) d'exemple créée(s).")

        created = 0
        course_photos = 0
        for data in COURSES:
            # Pas d'URL factice : le contenu se configure dans l'admin (fichier ou lien réel).
            payload = {**data, "course_url": ""}
            obj, was_created = Course.objects.get_or_create(title=data["title"], defaults=payload)
            created += was_created
            # Nettoie les anciens liens example.com laissés par une seed précédente.
            if obj.course_url and "example.com" in obj.course_url:
                obj.course_url = ""
                obj.save(update_fields=["course_url"])
            cover = COURSE_DEMO_IMAGES.get(data["title"])
            if cover and _attach_demo_image(obj.image, cover):
                course_photos += 1
            en = COURSES_EN.get(data["title"])
            if en and fill_en(obj, en):
                obj.save(update_fields=[f"{k}_en" for k in en])
                translated += 1
        self.stdout.write(f"Cours : {created} créé(s), {course_photos} image(s) ajoutée(s).")

        created = 0
        blog_photos = 0
        for title, excerpt, tags, days_ago, featured, content in DEMO_POSTS:
            obj, was_created = Post.objects.get_or_create(
                title=title,
                defaults={
                    "excerpt": excerpt,
                    "content": content,
                    "tags": tags,
                    "is_featured": featured,
                    "published_at": timezone.now() - timedelta(days=days_ago),
                },
            )
            created += was_created
            cover = BLOG_DEMO_IMAGES.get(title)
            if cover and _attach_demo_image(obj.cover, cover):
                blog_photos += 1
            en = POSTS_EN.get(title)
            if en and fill_en(obj, en):
                obj.save(update_fields=[f"{k}_en" for k in en])
                translated += 1
        self.stdout.write(f"Articles : {created} créé(s), {blog_photos} image(s) ajoutée(s).")

        if translated:
            self.stdout.write(self.style.SUCCESS(f"Traductions anglaises : {translated} enregistrement(s) complété(s)."))
        self.stdout.write(self.style.SUCCESS("Données de démonstration chargées."))
