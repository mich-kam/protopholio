"""
Traductions anglaises du contenu de démonstration (seed_demo).

Les textes français restent la source dans seed_demo.py ; ici on fournit les
équivalents anglais pour les colonnes modeltranslation (*_en). La commande
seed remplit uniquement les champs anglais encore vides (idempotent).
"""

PROFILE_EN = {
    "headline": "Web developer, databases & cybersecurity",
    "roles": "Web developer, Cybersecurity specialist, Networks & CCTV, Online instructor",
    "tagline": (
        "With a Bachelor's degree in Computer Science, I build web applications with Python, PHP "
        "and JavaScript, secure networks and systems, and share my knowledge "
        "through online courses."
    ),
    "about": (
        "Holding a Bachelor's degree in Computer Science, I trained in "
        "software development, databases, data processing, IT support, "
        "video surveillance (CCTV) and networking.\n\n"
        "I have practical skills in Python, PHP, JavaScript, HTML5, CSS3, MySQL "
        "and SQL, gained through internships and academic projects. My path has "
        "helped me grow in web application development, database "
        "management, data analysis, troubleshooting and end-user "
        "support.\n\n"
        "Passionate about cybersecurity, I focus on protecting networks, "
        "web applications and data, and on helping users build better "
        "digital habits.\n\n"
        "Curious, thorough and a fast learner, I enjoy working in a team "
        "and under pressure to deliver reliable solutions."
    ),
    "location": "Kinshasa, DRC",
    "languages": "French (C2) · Swahili (native) · Lingala (C1) · English (B2)",
}

# title_fr -> (title_en, description_en)
SERVICES_EN = {
    "Développement web & applications": (
        "Web & application development",
        "Custom web applications with Python, PHP, JavaScript, HTML5 and CSS3: "
        "client, order, student or inventory management.",
    ),
    "Bases de données & analyse de données": (
        "Databases & data analysis",
        "MySQL / SQL database design and administration, application data management, "
        "processing and early-stage data analysis.",
    ),
    "Réseaux informatiques": (
        "Computer networks",
        "Local network (LAN) installation and configuration: cabling, routers, switches, "
        "IP addressing, resource sharing and maintenance.",
    ),
    "Vidéosurveillance (CCTV)": (
        "Video surveillance (CCTV)",
        "IP and analog camera installation (Hikvision), DVR / NVR setup, "
        "wiring, commissioning and fault diagnosis.",
    ),
    "Cybersécurité": (
        "Cybersecurity",
        "Securing your networks, web applications and data: best practices, "
        "hardened configurations and user awareness.",
    ),
    "Support & maintenance informatique": (
        "IT support & maintenance",
        "Workstation and system troubleshooting, equipment maintenance, user "
        "assistance and fast incident resolution.",
    ),
    "Formation en ligne": (
        "Online training",
        "Practical courses in programming and databases, to follow at your own pace "
        "from your personal dashboard.",
    ),
}

FAQS_EN = {
    "Comment accéder à un cours après l'avoir acheté ?": (
        "How do I access a course after buying it?",
        "As soon as your order is confirmed, the course appears in your “My courses” area. "
        "Just sign in to open or download it whenever you like.",
    ),
    "Puis-je suivre un cours sur mon téléphone ?": (
        "Can I take a course on my phone?",
        "Yes. The site is designed for phones, tablets and computers. "
        "Downloadable files depend on the course: each course page lists what is included.",
    ),
    "Comment obtenir un reçu pour mon achat ?": (
        "How do I get a receipt for my purchase?",
        "A receipt is available for every order in “My courses”. You can print it "
        "or save it as PDF from your browser. A confirmation is also sent by email.",
    ),
    "J'ai oublié mon mot de passe, que faire ?": (
        "I forgot my password — what should I do?",
        "On the sign-in page, click “Forgot password?”, enter your email address "
        "and follow the link you receive to choose a new one.",
    ),
    "Comment vous contacter pour une mission ou un devis ?": (
        "How can I contact you for a project or a quote?",
        "Use the contact form at the bottom of the page, email me, or reach me "
        "by phone. I usually reply quickly.",
    ),
}

SKILLS_EN = {
    "Développement d'applications web": "Web application development",
    "Data Analytics": "Data Analytics",
    "Réseaux LAN, routeurs et switches": "LAN networks, routers and switches",
    "Vidéosurveillance IP (Hikvision, DVR/NVR)": "IP video surveillance (Hikvision, DVR/NVR)",
    "Support et maintenance informatique": "IT support and maintenance",
    "Sécurité des réseaux": "Network security",
    "Sécurité des applications web": "Web application security",
    "Protection des données": "Data protection",
    "Sensibilisation & bonnes pratiques": "Awareness & best practices",
    "Tests et vérification d'applications": "Application testing and verification",
    "Résolution de problèmes": "Problem solving",
}

# (kind, title_fr) -> (title_en, organization_en, description_en)
TIMELINE_EN = {
    ("experience", "Stagiaire en réseau informatique et vidéosurveillance"): (
        "IT network and CCTV intern",
        "AVOLIK – COTEBU / Friend's Building",
        "Installation of Hikvision IP cameras, cable runs and connections, network "
        "configuration and commissioning of the CCTV system (entrance, parking, computer room).",
    ),
    ("experience", "Stagiaire en informatique"): (
        "IT intern",
        "Global Technology",
        "IT support, equipment maintenance, user assistance, "
        "system and network configuration and troubleshooting.",
    ),
    ("education", "Licence LMD en Informatique"): (
        "Bachelor's degree (LMD) in Computer Science",
        "Hope Africa University of Burundi — Bujumbura",
        "",
    ),
    ("education", "Diplôme d'État en Commercial et gestion"): (
        "State diploma in Business and management",
        "Institut de l'Enano — Kindu, DRC",
        "",
    ),
    ("certification", "Programmation Web : HTML5, CSS3, JavaScript, PHP, MySQL et Python"): (
        "Web programming: HTML5, CSS3, JavaScript, PHP, MySQL and Python",
        "FFBF Center, Bujumbura",
        "",
    ),
    ("certification", "Réseaux informatiques"): (
        "Computer networks",
        "AVOLIK Bujumbura",
        "LAN networks, cabling, router and switch configuration, IP addressing, network maintenance.",
    ),
    ("certification", "Installation de vidéosurveillance"): (
        "CCTV installation",
        "Global Technologies of Burundi",
        "IP and analog cameras, DVR/NVR, cabling, CCTV maintenance, fault diagnosis.",
    ),
    ("certification", "Électricité de base"): (
        "Basic electricity",
        "Global Technology Bujumbura",
        "",
    ),
    ("certification", "Anglais"): (
        "English",
        "FFBF Center, Bujumbura",
        "",
    ),
}

PROJECTS_EN = {
    "Application de gestion scolaire": {
        "title": "School management application",
        "description": (
            "Design of an application for managing students, courses, "
            "teachers and academic results. Project completed at Hope Africa University."
        ),
        "technologies": "Application development, Databases, Programming",
    },
    "Application de gestion de restaurant": {
        "title": "Restaurant management application",
        "description": (
            "Web application for managing a restaurant's customers and orders. "
            "Personal project."
        ),
        "technologies": "HTML5, CSS3, JavaScript, PHP, MySQL",
    },
    "Réseau local d'entreprise": {
        "title": "Business local network",
        "description": (
            "Installation and configuration of a LAN with resource sharing, "
            "and equipment maintenance. Completed at Avolik Bujumbura."
        ),
        "technologies": "LAN, Cabling, Routers, Switches",
    },
    "Portfolio & plateforme de cours en ligne": {
        "title": "Portfolio & online course platform",
        "description": (
            "The site you are visiting: a dynamic portfolio paired with a course sales "
            "platform (authentication, orders, personal dashboard, administration)."
        ),
        "technologies": "Python, Django, Tailwind CSS, PostgreSQL",
    },
}

COURSES_EN = {
    "Python pour débutants": {
        "title": "Python for beginners",
        "short_description": "Learn Python basics step by step, with hands-on exercises.",
        "description": (
            "A complete course to get started with Python programming.\n\n"
            "Topics covered: variables, conditions, loops, functions, lists and dictionaries, "
            "reading and writing files, and a final mini-project."
        ),
        "duration": "6 h of content · 12 lessons",
        "learning_outcomes": (
            "Understand variables, types and operators\n"
            "Write conditions and loops\n"
            "Create and reuse functions\n"
            "Work with lists, dictionaries and files\n"
            "Complete a full mini-project"
        ),
        "requirements": "No prerequisites — a computer and curiosity are enough.",
    },
    "HTML, CSS et JavaScript : créer son premier site": {
        "title": "HTML, CSS and JavaScript: build your first website",
        "short_description": "Web fundamentals to build a modern, responsive site.",
        "description": (
            "Discover how the web works and build your first site from scratch.\n\n"
            "HTML5 structure, CSS3 styling, responsive layout and interactivity "
            "with JavaScript."
        ),
        "duration": "4 h of content · 8 lessons",
        "learning_outcomes": (
            "Structure a page with HTML5\n"
            "Style with CSS3\n"
            "Make a site responsive\n"
            "Add interactivity with JavaScript"
        ),
        "requirements": "Basic computer and web browser skills.",
    },
    "Bases de données avec MySQL et SQL": {
        "title": "Databases with MySQL and SQL",
        "short_description": "Model, query and administer a relational database.",
        "description": (
            "Learn to design reliable databases.\n\n"
            "Modeling, SELECT / INSERT / UPDATE / DELETE queries, joins, "
            "aggregations and best practices."
        ),
        "duration": "5 h of content · 10 lessons",
        "learning_outcomes": (
            "Model a relational database\n"
            "Write SELECT, INSERT, UPDATE and DELETE queries\n"
            "Master joins and aggregations\n"
            "Apply sound design practices"
        ),
        "requirements": "Basic computer literacy.",
    },
    "Cybersécurité : les bases pour se protéger": {
        "title": "Cybersecurity: the basics to stay safe",
        "short_description": "Understand common threats and build everyday security habits.",
        "description": (
            "An accessible introduction to cybersecurity, for individuals and small organizations alike.\n\n"
            "Phishing, passwords, Wi-Fi networks, backups: you will learn to recognize the most "
            "common risks and protect yourself in practice."
        ),
        "duration": "3 h of content · 6 lessons",
        "learning_outcomes": (
            "Understand the main threats (phishing, malware)\n"
            "Create and manage strong passwords\n"
            "Secure your Wi-Fi network and devices\n"
            "Spot and avoid online scams\n"
            "Set up reliable backups"
        ),
        "requirements": "No technical prerequisites.",
    },
}

POSTS_EN = {
    "5 réflexes pour des mots de passe vraiment solides": {
        "title": "5 habits for truly strong passwords",
        "excerpt": (
            "A weak password is attackers' favorite entry point. Here are five simple habits "
            "to protect all your accounts."
        ),
        "tags": "Cybersecurity, Best practices",
        "content": """Passwords are still the first barrier between a stranger and your accounts. Yet **123456** and **password** remain among the most used. Here are five habits to adopt today.

## 1. Prefer length over complexity

A password of **14 characters or more** is much harder to guess than a short one packed with symbols. A passphrase works very well: four or five unrelated words, for example `blue-horse-laptop-monday`.

## 2. A different password for every account

When a site is breached, stolen passwords are tried everywhere else (email, social networks, banking). Reusing the same password hands over the key to your whole digital life to whoever finds a single one.

## 3. Use a password manager

Nobody can remember dozens of long, unique passwords. A **password manager** generates them, stores them encrypted and fills them for you. You only need to remember one very strong master password.

## 4. Turn on two-factor authentication

Two-step verification (app or SMS code, security key) blocks access even if your password is stolen. Enable it at least on your email, social networks and financial services.

## 5. Never share your password

No serious service will ask for it by message, call or email. If someone demands it, it is a scam attempt.

> **Takeaway:** length, uniqueness, a manager, two-factor authentication, discretion. Five habits, ten minutes to set up, and your accounts are far better protected.
""",
    },
    "Phishing : comment reconnaître un message piégé": {
        "title": "Phishing: how to spot a trap message",
        "excerpt": (
            "Fake emails, SMS and WhatsApp messages: learn the warning signs and the right "
            "reflexes before you click."
        ),
        "tags": "Cybersecurity, Awareness",
        "content": """**Phishing** means impersonating a trusted entity (bank, carrier, administration, social network) to push you into giving a password, bank details or installing malware. It is one of the most common attack entry points today.

## Warning signs

- **Urgency or threats**: “your account will be locked in 24 h”, “immediate action required”.
- **Suspicious sender**: the address looks real but has a typo or a strange domain.
- **Misleading links**: the displayed text is not the real destination. Hover without clicking to see the true URL.
- **Unexpected attachments**: invoice, résumé, “important document” you were not expecting.
- **Typos and odd tone**: a real official message is rarely poorly written or overly familiar.
- **Requests for sensitive data**: a serious service never asks for your password or secret code.

## What to do with a suspicious message

1. **Click nothing** and do not open the attachment.
2. **Verify through another channel**: open the official site yourself (by typing the address) or call the service on its usual number.
3. **Report and delete** the message.
4. If you already clicked or entered information: **change the password immediately**, enable two-factor authentication and warn your bank if financial data is involved.

## A simple reflex

Before clicking, ask three questions: *Was I expecting this message? Is the sender really who they claim to be? What am I being pushed to do, and why so fast?*

When in doubt, do not click: take a minute to verify. That minute can save you weeks of trouble.
""",
    },
    "Sécuriser son réseau Wi-Fi à la maison ou au bureau": {
        "title": "Secure your home or office Wi-Fi network",
        "excerpt": (
            "Seven simple settings to stop strangers from using your connection — or worse, "
            "spying on your network."
        ),
        "tags": "Cybersecurity, Networks",
        "content": """A poorly protected Wi-Fi network lets anyone in range use your connection — or even spy on traffic. A few settings are enough to close the door.

## 1. Change the router admin credentials

Default admin passwords (“admin / admin”) are widely known. Right after install, set a **unique, long** administration password.

## 2. Choose modern encryption

In Wi-Fi settings, enable **WPA3** if your hardware supports it, otherwise **WPA2 (AES)**. Never use **WEP** or an open network without a password: they are trivially broken.

## 3. Use a strong Wi-Fi password

A passphrase of at least 16 characters. Avoid family names, company names or phone numbers.

## 4. Create a guest network

Visitors, connected devices (cameras, TVs, bulbs) and work devices should not share the same network. A **guest network** isolates those uses: if one device is compromised, the rest stays protected.

## 5. Disable what you do not need

- **WPS** (button or 8-digit code login): a known weakness.
- **Remote administration** of the router, if you do not use it.

## 6. Update the firmware

Vendors regularly fix flaws. Check router updates (or enable automatic updates) and replace hardware that is no longer supported.

## 7. Watch connected devices

The router interface lists connected devices. An unknown device? Change the Wi-Fi password.

> **At the office**, add a golden rule: a different Wi-Fi password for employees and for guests, and a change whenever a collaborator leaves the company.
""",
    },
    "Django : 7 réglages de sécurité à vérifier avant le déploiement": {
        "title": "Django: 7 security settings to check before deploy",
        "excerpt": (
            "Django is safe by default on many points, but production still needs a few precise "
            "settings. My checklist."
        ),
        "tags": "Django, Cybersecurity, Development",
        "content": """A Django site is safe by default on many points (CSRF protection, template escaping, password hashing…). But production still needs a few precise settings. Here is my checklist.

## 1. `DEBUG = False`

Debug mode shows sensitive details (paths, settings, SQL queries) on errors. **Never in production.**

## 2. A secret `SECRET_KEY`

It signs sessions and tokens. Read it from an **environment variable**, never commit it, and rotate it if it leaked.

## 3. `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`

List only your real domains. That blocks forged `Host` header attacks.

## 4. HTTPS everywhere

```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

Behind a proxy (Render, Heroku), add `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`.

## 5. Run the built-in check

```
python manage.py check --deploy
```

Django reviews your settings and flags what is missing. It is free: use it before every go-live.

## 6. Protect private files

Reserved files (paid courses, documents) must not be served by a public URL. Go through a view that **checks permissions** before sending the file.

## 7. Keep dependencies updated

Watch Django and library versions: security patches are published regularly.

> None of these settings is complicated. Forgetting them is what costs dearly.
""",
    },
}


def fill_en(obj, fields: dict) -> bool:
    """Écrit les champs *_en encore vides. Retourne True si quelque chose a changé."""
    changed = False
    for name, value in fields.items():
        if value is None:
            continue
        attr = f"{name}_en"
        current = getattr(obj, attr, None)
        if (current is None or current == "") and value != "":
            setattr(obj, attr, value)
            changed = True
    return changed
