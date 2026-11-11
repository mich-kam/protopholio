"""
Génère locale/en_import.txt à partir de locale/untranslated.txt + le dictionnaire EN.

    python tools/build_en_import.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "locale" / "untranslated.txt"
OUT = ROOT / "locale" / "en_import.txt"

# msgid français (sans le numéro) -> traduction anglaise
# Pour les pluriels : « forme1 ||| forme2 »
TRANSLATIONS: dict[str, str] = {
    "%(name)s, %(headline)s. Découvrez mes projets, mes services et mes cours en ligne.": (
        "%(name)s, %(headline)s. Discover my projects, services and online courses."
    ),
    "%(counter)s article ||| %(counter)s articles": "%(counter)s article ||| %(counter)s articles",
    "%(counter)s avis ||| %(counter)s avis": "%(counter)s review ||| %(counter)s reviews",
    "%(counter)s cours ||| %(counter)s cours": "%(counter)s course ||| %(counter)s courses",
    "%(counter)s étoile ||| %(counter)s étoiles": "%(counter)s star ||| %(counter)s stars",
    "%(minutes)s min": "%(minutes)s min",
    "%(minutes)s min de lecture": "%(minutes)s min read",
    "%(n)s sur 5": "%(n)s out of 5",
    "&larr; Article précédent": "&larr; Previous article",
    "&larr; Mes cours": "&larr; My courses",
    "&larr; Précédent": "&larr; Previous",
    "&larr; Retour au cours": "&larr; Back to course",
    "&larr; Retour au site": "&larr; Back to site",
    "&larr; Retour à la connexion": "&larr; Back to sign in",
    "&larr; Retour à mon compte": "&larr; Back to my account",
    "(simulation)": "(simulation)",
    ". Tous droits réservés.": ". All rights reserved.",
    ". Une confirmation sera envoyée à cette adresse.": ". A confirmation will be sent to this address.",
    "./verifier --domaines-de-securite": "./check --security-domains",
    ": aucun paiement n'est nécessaire. Confirmez simplement votre inscription.": (
        ": no payment is required. Simply confirm your enrollment."
    ),
    "Accueil": "Home",
    "Accès": "Access",
    "Accès immédiat après la commande": "Instant access after purchase",
    "Accès immédiat après validation.": "Instant access after confirmation.",
    "Accéder": "Open",
    "Accéder au contenu": "Access the content",
    "Accéder au cours": "Access the course",
    "Acheter ce cours": "Buy this course",
    "Achetez un cours et retrouvez-le à vie dans votre espace « Mes cours ».": (
        "Buy a course and keep lifetime access in your “My courses” area."
    ),
    "Acheté le %(date)s": "Purchased on %(date)s",
    "Acquis": "Owned",
    "Actions": "Actions",
    "Administration": "Administration",
    "Adresse e-mail": "Email address",
    "Afficher le mot de passe": "Show password",
    "Aller au contenu": "Skip to content",
    "Aller à": "Go to",
    "Aller à… une section, une page, une action": "Go to… a section, page, or action",
    "Annulée": "Cancelled",
    "Anti-spam sans espionnage": "Anti-spam without tracking",
    "Aperçu réservé à l'administration : cet article n'est pas (encore) visible du public.": (
        "Admin preview only: this article is not (yet) visible to the public."
    ),
    "Application web, réseau, vidéosurveillance ou formation : décrivez votre besoin, je vous réponds rapidement.": (
        "Web app, network, CCTV or training: describe your need and I’ll reply quickly."
    ),
    "Applications web": "Web applications",
    "Apprenez avec moi": "Learn with me",
    "Après plusieurs échecs, la connexion à un compte est temporairement bloquée : cela rend les attaques par force brute inefficaces.": (
        "After several failed attempts, sign-in is temporarily locked: that makes brute-force attacks ineffective."
    ),
    "Article suivant &rarr;": "Next article &rarr;",
    "Articles &amp; tutoriels": "Articles &amp; tutorials",
    "Articles et tutoriels sur la cybersécurité, le développement web et les réseaux.": (
        "Articles and tutorials on cybersecurity, web development and networking."
    ),
    "Articles et tutoriels sur la cybersécurité, le développement web, les réseaux et les bonnes pratiques numériques.": (
        "Articles and tutorials on cybersecurity, web development, networking and digital best practices."
    ),
    "Articles sur la cybersécurité, le développement web et les réseaux.": (
        "Articles on cybersecurity, web development and networking."
    ),
    "Aucun article": "No articles",
    "Aucun article pour le moment": "No articles yet",
    "Aucun cours ne correspond à votre recherche": "No courses match your search",
    "Aucun projet publié pour le moment.": "No projects published yet.",
    "Aucun résultat": "No results",
    "Aucun résultat. Essayez un autre mot.": "No results. Try another keyword.",
    "Aucun système n'est invulnérable : la sécurité est un travail continu, fait de mises à jour et de vigilance.": (
        "No system is invulnerable: security is ongoing work of updates and vigilance."
    ),
    "Aucun élément pour le moment.": "Nothing here yet.",
    "Aucune compétence renseignée pour le moment.": "No skills listed yet.",
    "Aucune donnée bancaire": "No card data stored",
    "Autres articles": "More articles",
    "Avancé": "Advanced",
    "Avis des apprenants": "Learner reviews",
    "Basculer le thème clair / sombre": "Toggle light / dark theme",
    "Base de données": "Database",
    "Bases de données & données": "Databases & data",
    "Bienvenue %(username)s ! Votre compte a bien été créé.": (
        "Welcome %(username)s! Your account has been created."
    ),
    "Blog": "Blog",
    "Blog &amp; articles": "Blog &amp; articles",
    "Blog — %(name)s": "Blog — %(name)s",
    "Blog — flux RSS": "Blog — RSS feed",
    "Bonjour %(name)s": "Hello %(name)s",
    "Bonjour, je suis": "Hello, I am",
    "Bonjour, je vous contacte depuis votre site.": "Hello, I’m reaching out from your website.",
    "Capture d'écran du projet": "Project screenshot",
    "Carte bancaire (simulation)": "Bank card (simulation)",
    "Catalogue de cours en ligne : programmation, bases de données, web.": (
        "Online course catalog: programming, databases, web."
    ),
    "Catalogue de cours en ligne : programmation, bases de données, web. Achetez un cours et retrouvez-le à vie dans votre espace personnel.": (
        "Online course catalog: programming, databases, web. Buy a course and keep lifetime access in your personal dashboard."
    ),
    "Catalogue des cours": "Course catalog",
    "Ce cours est": "This course is",
    "Ce cours inclut": "This course includes",
    "Ce cours vous a plu ?": "Did you enjoy this course?",
    "Ce lien a expiré ou a déjà été utilisé.": "This link has expired or has already been used.",
    "Ce que je peux faire pour vous": "What I can do for you",
    "Ce que vous allez apprendre": "What you will learn",
    "Ce que vous avez aimé, ce qui pourrait être amélioré…": (
        "What you liked, what could be improved…"
    ),
    "Ce site ne collecte ni ne stocke aucun numéro de carte bancaire.": (
        "This site never collects or stores any card numbers."
    ),
    "Certification": "Certification",
    "Certifications &amp; formations courtes": "Certifications &amp; short courses",
    "Cette adresse e-mail est déjà utilisée par un autre compte.": (
        "This email address is already used by another account."
    ),
    "Cette page est introuvable": "This page could not be found",
    "Changer de thème": "Change theme",
    "Changez-le régulièrement pour protéger votre compte.": (
        "Change it regularly to protect your account."
    ),
    "Chaque formulaire embarque un jeton unique qui empêche un site tiers d'agir à votre place.": (
        "Every form embeds a unique token that stops a third-party site from acting on your behalf."
    ),
    "Chercher": "Search",
    "Choisir un nouveau mot de passe": "Choose a new password",
    "Choisissez un mot de passe solide.": "Choose a strong password.",
    "Choisissez une note de 1 à 5 étoiles.": "Choose a rating from 1 to 5 stars.",
    "Cliquez sur le lien reçu pour choisir un nouveau mot de passe. Pensez à vérifier vos courriers indésirables si vous ne voyez rien arriver dans quelques minutes.": (
        "Click the link you receive to choose a new password. Check your spam folder if nothing arrives within a few minutes."
    ),
    "Code source": "Source code",
    "Commande": "Order",
    "Commande au nom de": "Order for",
    "Comment ce site protège vos données": "How this site protects your data",
    "Comment je travaille": "How I work",
    "Comment puis-je vous aider ?": "How can I help you?",
    "Compte": "Account",
    "Compétences": "Skills",
    "Confirmation de votre commande %(reference)s": "Confirmation of your order %(reference)s",
    "Connectez-vous pour accéder à vos cours.": "Sign in to access your courses.",
    "Connexion": "Sign in",
    "Connexion chiffrée (HTTPS)": "Encrypted connection (HTTPS)",
    "Contact": "Contact",
    "Content de vous revoir": "Welcome back",
    "Contenu à suivre en ligne": "Content to follow online",
    "Contrôle des accès et protection des informations sensibles.": (
        "Access control and protection of sensitive information."
    ),
    "Conçu avec Django &amp; Tailwind CSS": "Built with Django &amp; Tailwind CSS",
    "Copier": "Copy",
    "Copier l'e-mail": "Copy email",
    "Copier le lien": "Copy link",
    "E-mail copié !": "Email copied!",
    "Lien copié !": "Link copied!",
    "Agrandir la capture": "Enlarge screenshot",
    "Agrandir l'image": "Enlarge image",
    "Aperçu de l'image": "Image preview",
    "Sommaire": "Table of contents",
    "Cours": "Courses",
    "Cours achetés": "Courses purchased",
    "Cours acquis": "Courses owned",
    "Cours en ligne": "Online courses",
    "Cours gratuit": "Free course",
    "Cours réservés aux acheteurs": "Courses reserved for buyers",
    "Créer un compte": "Create an account",
    "Ctrl": "Ctrl",
    "Ctrl K": "Ctrl K",
    "Curriculum vitae de %(name)s : %(headline)s. Compétences, expériences, formations et projets.": (
        "Curriculum vitae of %(name)s: %(headline)s. Skills, experience, education and projects."
    ),
    "Cybersécurité": "Cybersecurity",
    "Cybersécurité, développement web, réseaux : des conseils concrets à appliquer tout de suite.": (
        "Cybersecurity, web development, networking: practical advice you can apply right away."
    ),
    "Cybersécurité, développement web, réseaux : des conseils concrets, sans jargon inutile.": (
        "Cybersecurity, web development, networking: practical advice, without useless jargon."
    ),
    "Date": "Date",
    "Demander un nouveau lien": "Request a new link",
    "Dernier achat": "Latest purchase",
    "Derniers articles": "Latest articles",
    "Des cours pratiques, accessibles à vie depuis votre espace personnel après achat.": (
        "Practical courses with lifetime access from your personal dashboard after purchase."
    ),
    "Des projets concrets et des cours en ligne pour apprendre à votre rythme.": (
        "Real projects and online courses to learn at your own pace."
    ),
    "Description": "Description",
    "Description du cours": "Course description",
    "Discuter sur WhatsApp": "Chat on WhatsApp",
    "Disponible pour de nouvelles missions": "Available for new projects",
    "Divulgation responsable": "Responsible disclosure",
    "Domaines d'expertise": "Areas of expertise",
    "Données": "Data",
    "Du développement d'applications à l'installation de réseaux, des solutions fiables, de la conception à la maintenance.": (
        "From application development to network installation — reliable solutions from design to maintenance."
    ),
    "Débutant": "Beginner",
    "Déconnexion": "Log out",
    "Découvrir": "Discover",
    "Découvrir des cours": "Browse courses",
    "Découvrir les cours": "Browse courses",
    "Découvrir mes cours": "Explore my courses",
    "Déjà inscrit ?": "Already registered?",
    "Démo": "Demo",
    "Développement": "Development",
    "Développement ou installation, avec des points d'étape réguliers.": (
        "Development or installation, with regular progress checkpoints."
    ),
    "Développement web": "Web development",
    "Développeur &amp; formateur": "Developer &amp; instructor",
    "E-mail": "Email",
    "E-mail envoyé": "Email sent",
    "Effacer": "Clear",
    "Effacer les filtres": "Clear filters",
    "En attente": "Pending",
    "En production, toutes les pages sont servies en HTTPS et le navigateur est invité à ne plus jamais utiliser HTTP (HSTS).": (
        "In production, every page is served over HTTPS and the browser is told never to use HTTP again (HSTS)."
    ),
    "En-têtes de sécurité": "Security headers",
    "Enregistrer": "Save",
    "Enregistrer les modifications": "Save changes",
    "Entrée": "Enter",
    "Entrées nettoyées": "Sanitized input",
    "Envoyer le lien": "Send the link",
    "Envoyer le message": "Send message",
    "Envoyer un message": "Send a message",
    "Erreur serveur": "Server error",
    "Essayez d'autres mots-clés ou retirez certains filtres.": (
        "Try other keywords or remove some filters."
    ),
    "Essayez un autre mot-clé ou retirez le filtre.": "Try another keyword or remove the filter.",
    "Expérience professionnelle": "Work experience",
    "FAQ": "FAQ",
    "Facturé à": "Billed to",
    "Fermer": "Close",
    "Fichier téléchargeable": "Downloadable file",
    "Fil d'Ariane": "Breadcrumb",
    "Filtrer par tag": "Filter by tag",
    "Finaliser ma commande": "Complete my order",
    "Flux RSS": "RSS feed",
    "Formation": "Education",
    "Gratuit": "Free",
    "Gratuits": "Free",
    "Historique des commandes": "Order history",
    "Identifiant de connexion : <strong>%(username)s</strong> · inscrit le %(joined)s": (
        "Sign-in ID: <strong>%(username)s</strong> · joined %(joined)s"
    ),
    "Ils m'ont fait confiance": "They trusted me",
    "Imprimer / enregistrer en PDF": "Print / save as PDF",
    "Indiquez votre adresse e-mail : nous vous enverrons un lien pour en choisir un nouveau.": (
        "Enter your email address and we’ll send a link to choose a new password."
    ),
    "Inscrivez-vous": "Sign up",
    "Inscrivez-vous pour acheter et suivre vos cours.": "Sign up to buy and follow your courses.",
    "Intermédiaire": "Intermediate",
    "Je conçois des applications web et je partage mon savoir-faire à travers des cours en ligne.": (
        "I design web applications and share my expertise through online courses."
    ),
    "Je vous présente une solution claire, un planning et un budget.": (
        "I present a clear solution, a timeline and a budget."
    ),
    "La page que vous cherchez n'existe pas ou a été déplacée.": (
        "The page you are looking for does not exist or has been moved."
    ),
    "La sécurité n'est pas un slogan. Voici, sans jargon, ce qui est réellement mis en place ici, et comment me signaler un problème si vous en trouvez un.": (
        "Security is not a slogan. Here is, without jargon, what is actually in place here, and how to report a problem if you find one."
    ),
    "La sécurité, pensée dès le départ": "Security, designed from the start",
    "Langages": "Languages",
    "Langages de programmation": "Programming languages",
    "Langue": "Language",
    "Langues": "Languages",
    "Le contenu de ce cours sera bientôt disponible.": "This course content will be available soon.",
    "Le formulaire de contact utilise un piège invisible (honeypot) plutôt qu'un traceur publicitaire.": (
        "The contact form uses an invisible honeypot instead of an advertising tracker."
    ),
    "Le paiement a échoué. Veuillez réessayer.": "Payment failed. Please try again.",
    "Les contenus saisis sont échappés à l'affichage et le contenu des articles est filtré pour bloquer tout code malveillant.": (
        "User input is escaped on display and article content is filtered to block malicious code."
    ),
    "Les cookies de session ne sont pas lisibles par JavaScript (HttpOnly), sont limités au même site (SameSite) et marqués « Secure » en production.": (
        "Session cookies are not readable by JavaScript (HttpOnly), limited to the same site (SameSite) and marked “Secure” in production."
    ),
    "Les fichiers de cours ne sont jamais accessibles par une URL publique : ils sont envoyés uniquement après vérification de l'achat.": (
        "Course files are never available via a public URL: they are sent only after purchase is verified."
    ),
    "Les mesures de sécurité appliquées à ce site : chiffrement, mots de passe, protection des comptes, des cours et des commandes. Comment signaler une vulnérabilité.": (
        "Security measures on this site: encryption, passwords, account, course and order protection. How to report a vulnerability."
    ),
    "Les mesures de sécurité réellement appliquées à ce site, et comment signaler une vulnérabilité.": (
        "The security measures actually applied on this site, and how to report a vulnerability."
    ),
    "Les mots de passe ne sont jamais stockés en clair : seul un hachage PBKDF2 salé est conservé, et les mots de passe trop faibles ou courants sont refusés.": (
        "Passwords are never stored in plain text: only a salted PBKDF2 hash is kept, and weak or common passwords are rejected."
    ),
    "Les premiers articles arrivent bientôt.": "The first articles are coming soon.",
    "Les premiers cours arrivent bientôt.": "The first courses are coming soon.",
    "Lien invalide": "Invalid link",
    "Limitation des tentatives de connexion": "Sign-in attempt limiting",
    "Lire l'article": "Read the article",
    "Livraison &amp; suivi": "Delivery &amp; follow-up",
    "Localisation": "Location",
    "Me contacter": "Contact me",
    "Merci ! Votre avis a bien été enregistré.": "Thank you! Your review has been saved.",
    "Merci ! Votre message a bien été envoyé, je vous répondrai rapidement.": (
        "Thank you! Your message has been sent — I’ll reply soon."
    ),
    "Merci ! Votre message a bien été envoyé.": "Thank you! Your message has been sent.",
    "Merci de me la signaler en privé avant toute publication, avec le plus de détails possible (page concernée, étapes pour reproduire). Je m'engage à accuser réception rapidement et à corriger le problème dans les meilleurs délais. Merci de ne pas accéder aux données d'autres utilisateurs.": (
        "Please report it privately before any publication, with as much detail as possible (page involved, steps to reproduce). I commit to acknowledging receipt quickly and fixing the issue as soon as possible. Please do not access other users’ data."
    ),
    "Merci pour votre confiance.": "Thank you for your trust.",
    "Mes cours": "My courses",
    "Mes cours achetés": "My purchased courses",
    "Mes informations": "My details",
    "Mes projets": "My projects",
    "Message": "Message",
    "Mettre à jour mon avis": "Update my review",
    "Mobile Money (simulation)": "Mobile Money (simulation)",
    "Mode démonstration :": "Demo mode:",
    "Modifier le mot de passe": "Change password",
    "Mon CV": "My résumé",
    "Mon CV (PDF)": "My résumé (PDF)",
    "Mon compte": "My account",
    "Mon cours": "My course",
    "Mon espace": "My dashboard",
    "Mon parcours et mes compétences": "My background and skills",
    "Montant": "Amount",
    "Mot de passe": "Password",
    "Mot de passe modifié": "Password changed",
    "Mot de passe oublié": "Forgot password",
    "Mot de passe oublié ?": "Forgot password?",
    "Mots de passe hachés": "Hashed passwords",
    "Mots de passe robustes, mises à jour, segmentation et sauvegardes.": (
        "Strong passwords, updates, segmentation and backups."
    ),
    "Moyen de paiement": "Payment method",
    "Méthode": "Method",
    "Méthodes": "Methods",
    "Navigation": "Navigation",
    "Navigation principale": "Main navigation",
    "Ne pas remplir": "Leave blank",
    "Niveau": "Level",
    "Niveau %(level)s": "Level %(level)s",
    "Niveau moyen par domaine :": "Average level by area:",
    "Nom": "Last name",
    "Nom d’utilisateur ou e-mail": "Username or email",
    "Note": "Rating",
    "Note : %(rating)s sur 5": "Rating: %(rating)s out of 5",
    "Nouveau": "New",
    "Nouveau mot de passe": "New password",
    "Objet de votre message": "Subject of your message",
    "Obtenir le cours": "Get the course",
    "On définit ensemble votre besoin, vos contraintes et vos délais.": (
        "Together we define your needs, constraints and deadlines."
    ),
    "Outils & méthodes": "Tools & methods",
    "Ouvrir": "Open",
    "Ouvrir le cours en ligne": "Open the online course",
    "Ouvrir le menu": "Open menu",
    "Page %(number)s sur %(pages)s": "Page %(number)s of %(pages)s",
    "Page introuvable": "Page not found",
    "Pages privées non indexées": "Private pages not indexed",
    "Pagination": "Pagination",
    "Paiement": "Payment",
    "Paiement confirmé ! Commande n° %(reference)s. Bon apprentissage !": (
        "Payment confirmed! Order #%(reference)s. Happy learning!"
    ),
    "Paiement effectué en mode démonstration : aucun montant n'a été réellement débité.": (
        "Payment completed in demo mode: no amount was actually charged."
    ),
    "Palette de commandes": "Command palette",
    "Parcourez le catalogue pour commencer à apprendre.": "Browse the catalog to start learning.",
    "Partager :": "Share:",
    "Partager sur Facebook": "Share on Facebook",
    "Partager sur LinkedIn": "Share on LinkedIn",
    "Partager sur WhatsApp": "Share on WhatsApp",
    "Pas encore d'avis sur ce cours. Les apprenants qui l'ont suivi peuvent donner le leur depuis leur espace.": (
        "No reviews for this course yet. Learners who took it can leave theirs from their dashboard."
    ),
    "Pas encore de compte ?": "Don’t have an account yet?",
    "PayPal (simulation)": "PayPal (simulation)",
    "Payants": "Paid",
    "Payer %(price)s %(symbol)s": "Pay %(price)s %(symbol)s",
    "Payée": "Paid",
    "Photo de": "Photo of",
    "Plan du site": "Sitemap",
    "Plus récents": "Newest",
    "Portfolio": "Portfolio",
    "Portfolio &amp; cours en ligne": "Portfolio &amp; online courses",
    "Portfolio, projets et cours en ligne.": "Portfolio, projects and online courses.",
    "Portrait de": "Portrait of",
    "Pour aller plus loin": "Go further",
    "Pour des raisons de sécurité, un lien de réinitialisation ne fonctionne qu'une fois et pour une durée limitée.": (
        "For security reasons, a reset link works only once and for a limited time."
    ),
    "Prix": "Price",
    "Prix croissant": "Price: low to high",
    "Prix décroissant": "Price: high to low",
    "Projets": "Projects",
    "Proposition": "Proposal",
    "Protection CSRF": "CSRF protection",
    "Protection contre le détournement de clic, l'interprétation erronée de fichiers, les fuites de référent et l'accès non sollicité à la caméra, au micro ou à la position.": (
        "Protection against clickjacking, MIME sniffing, referrer leaks and unsolicited access to the camera, microphone or location."
    ),
    "Prénom": "First name",
    "Prérequis": "Prerequisites",
    "Publier mon avis": "Publish my review",
    "Questions fréquentes": "Frequently asked questions",
    "REÇU": "RECEIPT",
    "Radar des compétences par domaine": "Skills radar by area",
    "Rechercher": "Search",
    "Rechercher (Ctrl+K)": "Search (Ctrl+K)",
    "Rechercher un article": "Search articles",
    "Rechercher un article…": "Search articles…",
    "Rechercher un cours": "Search courses",
    "Rechercher un cours…": "Search courses…",
    "Rechercher une page ou une action": "Search a page or action",
    "Remonter en haut de page": "Back to top",
    "Renseignez votre présentation depuis l'espace d'administration.": (
        "Fill in your profile from the admin area."
    ),
    "Retour en haut de page": "Back to top of page",
    "Retour à l'accueil": "Back to home",
    "Retour à la connexion": "Back to sign in",
    "Retrouvez tout dans « Mes cours »": "Find everything in “My courses”",
    "Reçu": "Receipt",
    "Reçu disponible pour chaque achat": "Receipt available for every purchase",
    "Reçus et commandes privés": "Private receipts and orders",
    "Réalisation": "Delivery",
    "Récapitulatif": "Summary",
    "Référence": "Reference",
    "Références disponibles sur demande.": "References available on request.",
    "Réinitialiser les filtres": "Reset filters",
    "Réseau / serveur": "Network / server",
    "Réseaux": "Networks",
    "Réseaux & systèmes": "Networks & systems",
    "Résultats": "Results",
    "S'abonner avec un lecteur RSS": "Subscribe with an RSS reader",
    "S'inscrire": "Sign up",
    "S'inscrire gratuitement": "Sign up for free",
    "Saisissez votre mot de passe actuel puis le nouveau.": (
        "Enter your current password, then the new one."
    ),
    "Se connecter": "Sign in",
    "Se connecter pour acheter": "Sign in to buy",
    "Sensibilisation au phishing et aux bonnes pratiques : le maillon humain compte.": (
        "Phishing awareness and best practices: the human factor matters."
    ),
    "Services": "Services",
    "Sessions protégées": "Protected sessions",
    "Seuls les acheteurs d'un cours peuvent laisser un avis.": (
        "Only course buyers can leave a review."
    ),
    "Si un compte correspond à cette adresse, un e-mail vient d'être envoyé.": (
        "If an account matches this address, an email has just been sent."
    ),
    "Signaler par e-mail": "Report by email",
    "Statut :": "Status:",
    "Suivant &rarr;": "Next &rarr;",
    "Sujet": "Subject",
    "Support / maintenance": "Support / maintenance",
    "Sécurité": "Security",
    "Sécurité du site": "Site security",
    "Technologies maîtrisées": "Technologies mastered",
    "Tests, sécurisation, mise en service et assistance après livraison.": (
        "Testing, hardening, go-live and post-delivery support."
    ),
    "Titre (A → Z)": "Title (A → Z)",
    "Total": "Total",
    "Total investi": "Total invested",
    "Total payé": "Total paid",
    "Tous les articles": "All articles",
    "Tous les niveaux": "All levels",
    "Tous les prix": "All prices",
    "Trier par": "Sort by",
    (
        "Trop de tentatives échouées. Par sécurité, la connexion est bloquée pendant encore "
        "%(minutes)d minute. Vous pouvez aussi réinitialiser votre mot de passe. ||| "
        "Trop de tentatives échouées. Par sécurité, la connexion est bloquée pendant encore "
        "%(minutes)d minutes. Vous pouvez aussi réinitialiser votre mot de passe."
    ): (
        "Too many failed attempts. For security, sign-in is locked for another "
        "%(minutes)d minute. You can also reset your password. ||| "
        "Too many failed attempts. For security, sign-in is locked for another "
        "%(minutes)d minutes. You can also reset your password."
    ),
    "Télécharger en PDF": "Download as PDF",
    "Télécharger le fichier": "Download the file",
    "Téléphone": "Phone",
    "Témoignages": "Testimonials",
    "Un compte existe déjà avec cette adresse e-mail.": (
        "An account already exists with this email address."
    ),
    "Un déroulé simple et transparent, de la première discussion à la mise en service.": (
        "A simple, transparent process from the first discussion to go-live."
    ),
    "Un projet en tête ? Parlons-en.": "Got a project in mind? Let’s talk.",
    "Un reçu n'est consultable que par son propriétaire. Pour tout autre visiteur, il n'existe tout simplement pas.": (
        "A receipt is only visible to its owner. For anyone else, it simply does not exist."
    ),
    "Un site, un réseau local ou un système de vidéosurveillance n'est fiable que s'il est protégé. J'intègre la sécurité à chaque projet : accès maîtrisés, configurations durcies, données sauvegardées et utilisateurs sensibilisés.": (
        "A website, local network or CCTV system is only reliable if it is protected. I build security into every project: controlled access, hardened configurations, backed-up data and informed users."
    ),
    "Une erreur est survenue de notre côté. Veuillez réessayer dans un instant.": (
        "Something went wrong on our side. Please try again in a moment."
    ),
    "Une question sur ce cours ?": "A question about this course?",
    "Une question sur un cours, une collaboration ou une opportunité ? Je lis chaque message.": (
        "A question about a course, a collaboration or an opportunity? I read every message."
    ),
    "Une question, un besoin ? Parlons-en.": "A question or a need? Let’s talk.",
    "Une sélection de projets réalisés pendant mes études, mes stages et à titre personnel.": (
        "A selection of projects completed during my studies, internships and personal work."
    ),
    "Utilisateurs": "Users",
    "Validation des données, authentification et protection contre les attaques courantes.": (
        "Input validation, authentication and protection against common attacks."
    ),
    "Validation manuelle": "Manual review",
    "Version PDF d'origine": "Original PDF version",
    "Vidéosurveillance": "Video surveillance",
    "Voir le reçu": "View receipt",
    "Voir les cours": "View courses",
    "Voir mes projets": "View my projects",
    "Voir mon CV complet": "View my full résumé",
    "Voir tous les articles": "View all articles",
    "Voir tout le catalogue": "View full catalog",
    "Vos informations ont été mises à jour.": "Your details have been updated.",
    "Votre avis": "Your review",
    "Votre avis a été mis à jour.": "Your review has been updated.",
    "Votre commande a déjà été enregistrée.": "Your order has already been recorded.",
    "Votre commentaire (facultatif)": "Your comment (optional)",
    "Votre contenu est disponible immédiatement et pour toujours.": (
        "Your content is available immediately and forever."
    ),
    "Votre espace, vos commandes et vos reçus sont exclus des moteurs de recherche.": (
        "Your dashboard, orders and receipts are excluded from search engines."
    ),
    "Votre mot de passe a été modifié.": "Your password has been changed.",
    "Votre nom": "Your name",
    "Votre note": "Your rating",
    "Votre retour aide les autres apprenants à choisir.": (
        "Your feedback helps other learners choose."
    ),
    "Vous aimerez aussi": "You may also like",
    "Vous avez trouvé une faille ?": "Found a vulnerability?",
    "Vous devez acheter ce cours pour le télécharger.": "You must buy this course to download it.",
    "Vous devez acheter ce cours pour y accéder.": "You must buy this course to access it.",
    "Vous n'avez encore acheté aucun cours": "You haven’t bought any courses yet",
    "Vous possédez déjà ce cours.": "You already own this course.",
    "Vous pouvez le modifier à tout moment.": "You can update it at any time.",
    "Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.": (
        "You can now sign in with your new password."
    ),
    "Vérifiez votre boîte mail": "Check your inbox",
    "Web": "Web",
    "WhatsApp": "WhatsApp",
    "acces/": "access/",
    "acheter/": "buy/",
    "article": "article",
    "avis/": "review/",
    "commande/": "order/",
    "comptes/": "accounts/",
    "connexion/": "login/",
    "contact/": "contact/",
    "cours/": "courses/",
    "cv/": "cv/",
    "dans « <strong>%(tag)s</strong> »": "in “<strong>%(tag)s</strong>”",
    "deconnexion/": "logout/",
    "developpeur.py": "developer.py",
    "developer.py": "developer.py",
    "Certifications": "Certifications",
    "développeur &amp; formateur": "developer &amp; instructor",
    "gratuit": "free",
    "index, follow": "index, follow",
    "inscription/": "register/",
    "le paiement est simulé, aucun montant n'est réellement débité.": (
        "payment is simulated — no amount is actually charged."
    ),
    "mon-espace/": "my-space/",
    "mot-de-passe/modifier/": "password/change/",
    "mot-de-passe/oublie/": "password/forgot/",
    "mot-de-passe/oublie/envoye/": "password/forgot/sent/",
    "mot-de-passe/reinitialise/": "password/reset/done/",
    "mot-de-passe/reinitialiser/": "password/reset/",
    "naviguer ·": "navigate ·",
    "noindex, nofollow": "noindex, nofollow",
    "ouvrir": "open",
    "pour l'ouvrir partout": "to open it anywhere",
    "pour « <strong>%(q)s</strong> »": "for “<strong>%(q)s</strong>”",
    "profil/": "profile/",
    "recu/": "receipt/",
    "securite.sh": "security.sh",
    "securite/": "security/",
    "security.txt": "security.txt",
    "telecharger/": "download/",
    "vous@exemple.com": "you@example.com",
    "À la une": "Featured",
    "À lire aussi": "Also read",
    "À propos": "About",
    "À propos de ce cours": "About this course",
    "À propos de l'auteur": "About the author",
    "Échange": "Discovery",
    "Échap": "Esc",
    "Écrire un e-mail": "Write an email",
    "Écrit par": "Written by",
    "Écrivez-moi": "Write to me",
    "Écrivez-moi, je vous répondrai rapidement.": "Write to me — I’ll reply quickly.",
    "Étape 1": "Step 1",
    "Étape 2": "Step 2",
    "Étape 3": "Step 3",
    "Étape 4": "Step 4",
    "Étapes de la commande": "Checkout steps",
}


def main() -> None:
    missing: list[str] = []
    lines_out: list[str] = []
    for raw in SRC.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        number, _, msgid = raw.partition("|")
        translation = TRANSLATIONS.get(msgid)
        if translation is None:
            missing.append(msgid)
            continue
        lines_out.append(f"{number}|{translation}")

    if missing:
        preview = "\n".join(f"  - {m!r}" for m in missing[:30])
        raise SystemExit(f"{len(missing)} msgid(s) sans traduction:\n{preview}")

    OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines_out)} lines to {OUT}")


if __name__ == "__main__":
    main()
