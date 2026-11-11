import json
import re
import tempfile
from datetime import datetime, timedelta, timezone as dt_timezone
from io import StringIO
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.management import CommandError, call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone, translation
from PIL import Image

from blog.models import Post

from .models import Profile, Project, Service, Skill, TimelineItem
from .radar import CENTER, RADIUS, build_radar
from .security_info import SECURITY_MEASURES
from .templatetags.ui import FILL_ICONS, STROKE_ICONS


def make_profile(**kwargs):
    defaults = {"full_name": "Michel Test", "headline": "Développeur", "email": "michel@example.com"}
    defaults.update(kwargs)
    return Profile.objects.create(**defaults)


def make_post(**kwargs):
    defaults = {"title": "Un article", "excerpt": "Résumé", "content": "Contenu"}
    defaults.update(kwargs)
    return Post.objects.create(**defaults)


class FrenchLocaleTestCase(TestCase):
    """Réactive le français après chaque test : LocaleMiddleware laisse la langue du dernier /en/ active."""

    def setUp(self):
        super().setUp()
        translation.activate(settings.LANGUAGE_CODE)

    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)
        super().tearDown()


class PhotoTests(FrenchLocaleTestCase):
    def test_default_photo_is_the_bundled_static_file(self):
        self.assertEqual(Profile(full_name="M", headline="D").photo_url, "/static/img/profile.jpg")

    def test_uploaded_photo_takes_precedence(self):
        self.assertEqual(Profile(full_name="M", headline="D", photo="profile/moi.jpg").photo_url, "/media/profile/moi.jpg")

    def test_photo_is_shown_in_hero_and_about_sections(self):
        make_profile()
        html = self.client.get(reverse("portfolio:home")).content.decode()
        self.assertGreaterEqual(html.count('src="/static/img/profile.jpg"'), 2)
        self.assertIn("Portrait de Michel Test", html)

    def test_share_image_is_the_generated_social_card(self):
        make_profile()
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, 'property="og:image" content="http://testserver/static/img/social-card.jpg"')
        self.assertContains(response, 'content="summary_large_image"')

    def test_photo_is_exposed_in_person_structured_data(self):
        make_profile()
        html = self.client.get(reverse("portfolio:home")).content.decode()
        data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
        self.assertEqual(data["image"], "http://testserver/static/img/profile.jpg")

    def test_the_bundled_photo_is_a_valid_clean_image(self):
        from django.conf import settings

        with Image.open(Path(settings.BASE_DIR, "static", "img", "profile.jpg")) as photo:
            self.assertEqual(photo.format, "JPEG")
            self.assertFalse(photo.getexif(), "la photo ne doit contenir aucune métadonnée (EXIF/GPS)")


class SocialCardCommandTests(FrenchLocaleTestCase):
    def test_command_writes_a_1200_by_630_jpeg(self):
        make_profile(roles="Développeur web, Spécialiste cybersécurité")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "card.jpg"
            with mock.patch("portfolio.management.commands.make_social_card.OUTPUT", target):
                call_command("make_social_card", stdout=StringIO())
            with Image.open(target) as card:
                self.assertEqual((card.format, card.size), ("JPEG", (1200, 630)))

    def test_command_requires_a_profile(self):
        with self.assertRaises(CommandError):
            call_command("make_social_card", stdout=StringIO())


class CVPageTests(FrenchLocaleTestCase):
    def setUp(self):
        call_command("seed_demo", stdout=StringIO())
        self.url = reverse("portfolio:cv")

    def test_cv_is_public_and_contains_the_essentials(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for expected in (
            "Kamango Lodi Michel",
            "michk2216@gmail.com",
            "Licence LMD en Informatique",
            "Stagiaire en informatique",
            "Application de gestion scolaire",
            "Télécharger en PDF",
            'src="/static/img/profile.jpg"',
        ):
            self.assertContains(response, expected)

    def test_cv_features_cybersecurity(self):
        response = self.client.get(self.url)
        self.assertContains(response, "cybersécurité")
        self.assertContains(response, "Sécurité des réseaux")  # compétence
        self.assertContains(response, "Domaines d'expertise")
        titles = [s.title for s in response.context["services"]]
        self.assertIn("Cybersécurité", titles)

    def test_cv_never_exposes_sensitive_personal_data(self):
        """Le CV d'origine contenait passeport, date de naissance et adresse : rien de tout cela ne doit sortir."""
        html = self.client.get(self.url).content.decode().lower()
        for secret in ("passeport", "op1566231", "21/01/2003", "lemba", "salongo", "état civil", "ngamba"):
            self.assertNotIn(secret, html)

    def test_cv_is_printable_without_site_chrome(self):
        html = self.client.get(self.url).content.decode()
        self.assertIn("@page { size: A4; margin: 0; }", html)
        self.assertIn("data-print", html)
        # Navigation, pied de page et boutons flottants portent la classe masquée à l'impression.
        self.assertGreaterEqual(html.count("no-print"), 4)

    def test_original_pdf_link_only_appears_when_a_pdf_was_uploaded(self):
        self.assertNotContains(self.client.get(self.url), "Version PDF d'origine")
        Profile.objects.update(cv_file="profile/cv/mon-cv.pdf")
        self.assertContains(self.client.get(self.url), "Version PDF d'origine")

    def test_cv_renders_with_an_empty_database(self):
        Profile.objects.all().delete()
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_languages_are_split_for_the_cv(self):
        profile = Profile(full_name="M", headline="D", languages="Français (C2) · Anglais (B2), Swahili (natif)")
        self.assertEqual(profile.languages_list, ["Français (C2)", "Anglais (B2)", "Swahili (natif)"])

    def test_hero_and_about_link_to_the_cv_page(self):
        html = self.client.get(reverse("portfolio:home")).content.decode()
        self.assertGreaterEqual(html.count(f'href="{self.url}"'), 2)


class SeededProfileTests(FrenchLocaleTestCase):
    def test_cybersecurity_is_part_of_the_seeded_profile(self):
        call_command("seed_demo", stdout=StringIO())
        profile = Profile.objects.get()
        self.assertIn("cybersécurité", profile.headline.lower())
        self.assertIn("cybersécurité", profile.about.lower())
        self.assertTrue(Skill.objects.filter(category=Skill.Category.SECURITY).exists())
        self.assertTrue(Service.objects.filter(icon=Service.Icon.SHIELD).exists())
        self.assertTrue(Post.objects.filter(tags__icontains="Cybersécurité").exists())

    def test_seed_is_idempotent_including_blog_posts(self):
        call_command("seed_demo", stdout=StringIO())
        count = Post.objects.count()
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(Post.objects.count(), count)
        self.assertGreaterEqual(count, 4)


class SecurityPageTests(FrenchLocaleTestCase):
    def test_page_lists_every_measure(self):
        make_profile()
        response = self.client.get(reverse("portfolio:security"))
        self.assertEqual(response.status_code, 200)
        for _icon, title, _text in SECURITY_MEASURES:
            self.assertContains(response, title)
        self.assertContains(response, "mailto:michel@example.com")
        self.assertContains(response, reverse("root:security_txt"))

    def test_page_works_without_profile_email(self):
        self.assertEqual(self.client.get(reverse("portfolio:security")).status_code, 200)

    def test_every_measure_has_a_known_icon(self):
        known = set(STROKE_ICONS) | set(FILL_ICONS)
        self.assertEqual({icon for icon, _t, _d in SECURITY_MEASURES} - known, set())

    def test_security_txt_follows_rfc_9116(self):
        make_profile()
        response = self.client.get("/.well-known/security.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        fields = dict(line.split(": ", 1) for line in response.content.decode().strip().splitlines())
        self.assertEqual(fields["Contact"], "mailto:michel@example.com")
        self.assertEqual(fields["Canonical"], "http://testserver/.well-known/security.txt")
        self.assertEqual(fields["Policy"], "http://testserver/securite/")
        expires = datetime.strptime(fields["Expires"], "%Y-%m-%dT%H:%M:%S.000Z").replace(tzinfo=dt_timezone.utc)
        self.assertGreater(expires, timezone.now() + timedelta(days=300))

    def test_security_txt_is_404_without_a_contact_email(self):
        self.assertEqual(self.client.get("/.well-known/security.txt").status_code, 404)
        make_profile(email="")
        self.assertEqual(self.client.get("/.well-known/security.txt").status_code, 404)

    def test_security_headers_are_present(self):
        response = self.client.get(reverse("portfolio:home"))
        self.assertEqual(response["Permissions-Policy"], "camera=(), microphone=(), geolocation=(), interest-cohort=()")
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["Referrer-Policy"], "same-origin")

    def test_security_headers_are_also_sent_on_error_pages(self):
        self.assertIn("Permissions-Policy", self.client.get("/page-inexistante/"))


class RadarTests(FrenchLocaleTestCase):
    @staticmethod
    def skills(*specs):
        return [Skill(name=f"s{i}", category=category, level=level) for i, (category, level) in enumerate(specs)]

    def test_needs_at_least_three_categories(self):
        C = Skill.Category
        self.assertIsNone(build_radar([]))
        self.assertIsNone(build_radar(self.skills((C.WEB, 80), (C.WEB, 60))))
        self.assertIsNone(build_radar(self.skills((C.WEB, 80), (C.DATA, 60))))

    def test_geometry_for_three_categories(self):
        C = Skill.Category
        radar = build_radar(self.skills((C.LANGUAGES, 100), (C.WEB, 50), (C.SECURITY, 0)))
        self.assertEqual(len(radar["axes"]), 3)
        self.assertEqual(len(radar["rings"]), 4)
        self.assertEqual(len(radar["polygon"].split()), 3)
        self.assertEqual([label["text"] for label in radar["labels"]], ["Langages", "Web", "Sécurité"])

        first_axis = radar["axes"][0]
        self.assertAlmostEqual(float(first_axis["x"]), CENTER, places=0)  # le premier axe pointe vers le haut
        self.assertAlmostEqual(float(first_axis["y"]), CENTER - RADIUS, places=0)
        self.assertAlmostEqual(float(radar["dots"][0]["y"]), CENTER - RADIUS, places=0)  # niveau 100 % = au bord
        self.assertEqual((radar["dots"][2]["x"], radar["dots"][2]["y"]), (radar["center"], radar["center"]))  # 0 % = centre

    def test_category_level_is_the_average_of_its_skills(self):
        C = Skill.Category
        radar = build_radar(self.skills((C.WEB, 80), (C.WEB, 60), (C.DATA, 50), (C.SECURITY, 40)))
        values = {label["text"]: label["value"] for label in radar["labels"]}
        self.assertEqual(values, {"Web": 70, "Données": 50, "Sécurité": 40})

    def test_points_stay_inside_the_chart(self):
        C = Skill.Category
        radar = build_radar(self.skills(*[(c, 100) for c in C.values]))
        for dot in radar["dots"]:
            self.assertTrue(0 <= float(dot["x"]) <= radar["size"] and 0 <= float(dot["y"]) <= radar["size"])

    def test_numbers_use_a_decimal_point_whatever_the_site_language(self):
        C = Skill.Category
        radar = build_radar(self.skills((C.LANGUAGES, 77), (C.WEB, 66), (C.SECURITY, 55)))
        values = [radar["center"]]
        values += [v for axis in radar["axes"] for v in axis.values()]
        values += [v for label in radar["labels"] for v in (label["x"], label["y"])]
        values += [v for dot in radar["dots"] for v in dot.values()]
        for value in values:
            self.assertIsInstance(value, str)
            self.assertNotIn(",", value)

    def test_rendered_svg_attributes_never_contain_decimal_commas(self):
        """
        Régression : en français, Django écrivait x="283,4". En SVG, la virgule sépare une liste de valeurs :
        les lettres des étiquettes étaient dispersées et les axes/points disparaissaient.
        """
        C = Skill.Category
        for name, category in (("Python", C.LANGUAGES), ("CSS", C.WEB), ("Pare-feu", C.SECURITY)):
            Skill.objects.create(name=name, category=category, level=63)
        html = self.client.get(reverse("portfolio:home")).content.decode()
        svg = html[html.index("<svg viewBox") : html.index("</svg>", html.index("<svg viewBox"))]
        attributes = re.findall(r'\b(?:x|y|cx|cy|x1|x2|y1|y2)="([^"]*)"', svg)
        self.assertGreater(len(attributes), 10)
        for value in attributes:
            self.assertNotIn(",", value, f"virgule décimale dans un attribut SVG : {value!r}")

    def test_home_renders_the_radar_only_when_there_is_enough_data(self):
        C = Skill.Category
        Skill.objects.create(name="Python", category=C.LANGUAGES, level=70)
        Skill.objects.create(name="CSS", category=C.WEB, level=70)
        html = self.client.get(reverse("portfolio:home")).content.decode()
        self.assertNotIn("Radar des compétences", html)
        Skill.objects.create(name="Sécurité web", category=C.SECURITY, level=60)
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, "Radar des compétences")
        self.assertIsNotNone(response.context["radar"])


class HomeBlogSectionTests(FrenchLocaleTestCase):
    def test_section_is_hidden_without_posts(self):
        self.assertNotContains(self.client.get(reverse("portfolio:home")), 'id="blog"')

    def test_latest_three_published_posts_are_shown(self):
        now = timezone.now()
        for i in range(5):
            make_post(title=f"Article {i}", published_at=now - timedelta(days=i))
        make_post(title="Brouillon", is_published=False)
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, 'id="blog"')
        self.assertEqual([p.title for p in response.context["latest_posts"]], ["Article 0", "Article 1", "Article 2"])
        self.assertNotContains(response, "Brouillon")


class SectionBandTests(FrenchLocaleTestCase):
    def test_home_sections_use_the_automatic_alternating_band_class(self):
        html = self.client.get(reverse("portfolio:home")).content.decode()
        ids = re.findall(r'<section id="([\w-]+)" class="band ', html)
        # Base vide : les sections facultatives (services, blog, témoignages, FAQ) sont masquées.
        self.assertEqual(ids, ["a-propos", "portfolio", "methode", "cours", "contact"])


class IconCoverageTests(FrenchLocaleTestCase):
    def test_new_icons_exist(self):
        for name in ("lock", "terminal", "users"):
            self.assertIn(name, STROKE_ICONS)

    def test_star_flags_filter(self):
        from .templatetags.ui import star_flags

        self.assertEqual(star_flags(4.4), [True] * 4 + [False])
        self.assertEqual(star_flags(4.5), [True] * 5)  # la demi-étoile monte...
        self.assertEqual(star_flags(2.5), [True] * 3 + [False] * 2)  # ...toujours (round() de Python donnerait 2)
        self.assertEqual(star_flags(3.5), [True] * 4 + [False])
        self.assertEqual(star_flags(5), [True] * 5)
        self.assertEqual(star_flags(0), [False] * 5)
        self.assertEqual(star_flags(None), [False] * 5)
        self.assertEqual(star_flags("abc"), [False] * 5)
        self.assertEqual(star_flags(99), [True] * 5)


class ProjectTimelineSanityTests(FrenchLocaleTestCase):
    def test_cv_lists_projects_and_timeline_from_the_database(self):
        Project.objects.create(title="Projet Phare", description="Une description", technologies="Python, Django")
        TimelineItem.objects.create(kind=TimelineItem.Kind.CERTIFICATION, title="Certificat X", period="2025")
        html = self.client.get(reverse("portfolio:cv")).content.decode()
        self.assertIn("Projet Phare", html)
        self.assertIn("Python · Django", html)
        self.assertIn("Certificat X", html)


class BilingualSiteTests(FrenchLocaleTestCase):
    def test_home_is_available_in_french_and_english(self):
        make_profile(headline="Développeur web", headline_en="Web developer")
        fr = self.client.get("/").content.decode()
        en = self.client.get("/en/").content.decode()
        self.assertIn('lang="fr"', fr)
        self.assertIn("Développeur web", fr)
        self.assertIn('lang="en"', en)
        self.assertIn("Web developer", en)
        self.assertIn('hreflang="en"', fr)
        self.assertIn('hreflang="fr"', en)

    def test_language_switcher_points_to_the_translated_path(self):
        response = self.client.get("/cours/")
        html = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn('href="/en/courses/"', html)
        self.assertIn('aria-label="Langue"', html)

    def test_translated_account_urls(self):
        self.assertEqual(self.client.get("/comptes/connexion/").status_code, 200)
        self.assertEqual(self.client.get("/en/accounts/login/").status_code, 200)
