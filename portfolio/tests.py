import html
import json
import re
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.urls import reverse

from courses.models import Course, Order

from .models import FAQ, ContactMessage, Profile, Project, Service, Skill, Testimonial, TimelineItem
from .seo import jsonld


def make_course(**kwargs):
    defaults = {
        "title": "Cours visible",
        "short_description": "s",
        "description": "d",
        "course_url": "https://example.com",
    }
    defaults.update(kwargs)
    return Course.objects.create(**defaults)


class HomePageTests(TestCase):
    def test_home_renders_without_any_data(self):
        response = self.client.get(reverse("portfolio:home"))
        self.assertEqual(response.status_code, 200)
        for anchor in ("accueil", "a-propos", "portfolio", "cours", "contact"):
            self.assertContains(response, f'id="{anchor}"')

    def test_home_shows_profile_projects_and_published_courses_only(self):
        Profile.objects.create(full_name="Michel Test", headline="Dev")
        Project.objects.create(title="Projet A", description="d", technologies="Python, Django")
        make_course(title="Cours visible")
        make_course(title="Cours brouillon", is_published=False)
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, "Michel Test")
        self.assertContains(response, "Projet A")
        self.assertContains(response, "Cours visible")
        self.assertNotContains(response, "Cours brouillon")

    def test_services_and_faq_are_listed_when_published(self):
        Service.objects.create(title="Service visible", description="d", icon="code")
        Service.objects.create(title="Service caché", description="d", is_published=False)
        FAQ.objects.create(question="Question visible ?", answer="Réponse visible")
        FAQ.objects.create(question="Question cachée ?", answer="x", is_published=False)
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, "Service visible")
        self.assertNotContains(response, "Service caché")
        self.assertContains(response, "Question visible ?")
        self.assertNotContains(response, "Question cachée ?")

    def test_empty_sections_are_hidden(self):
        response = self.client.get(reverse("portfolio:home"))
        self.assertNotContains(response, 'id="services"')
        self.assertNotContains(response, 'id="temoignages"')
        self.assertNotContains(response, 'id="faq"')

    def test_testimonials_section_appears_only_with_published_entries(self):
        Testimonial.objects.create(author_name="Alice", content="Très bon cours", is_published=False)
        self.assertNotContains(self.client.get(reverse("portfolio:home")), 'id="temoignages"')
        Testimonial.objects.create(author_name="Bob", author_role="Étudiant", content="Excellent formateur")
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, 'id="temoignages"')
        self.assertContains(response, "Excellent formateur")
        self.assertNotContains(response, "Très bon cours")

    def test_stats_are_real_and_zero_values_are_hidden(self):
        response = self.client.get(reverse("portfolio:home"))
        self.assertEqual(response.context["stats"], [])

        Project.objects.create(title="P1", description="d", technologies="x")
        Project.objects.create(title="P2", description="d", technologies="x")
        course = make_course()
        User = get_user_model()
        for name in ("a", "b"):
            Order.objects.create(
                user=User.objects.create_user(name, f"{name}@x.com", "pw"), course=course, amount=1, status="paid"
            )
        stats = dict(self.client.get(reverse("portfolio:home")).context["stats"])
        self.assertEqual(stats["Projets réalisés"], 2)
        self.assertEqual(stats["Cours en ligne"], 1)
        self.assertEqual(stats["Apprenants"], 2)
        self.assertNotIn("Certifications", stats)

    def test_skill_categories_follow_model_order(self):
        Skill.objects.create(name="Wifi", category=Skill.Category.SYSTEMS, level=50)
        Skill.objects.create(name="Python", category=Skill.Category.LANGUAGES, level=50)
        Skill.objects.create(name="CSS", category=Skill.Category.WEB, level=50)
        names = [s.name for s in self.client.get(reverse("portfolio:home")).context["skills"]]
        self.assertEqual(names, ["Python", "CSS", "Wifi"])

    def test_whatsapp_button_only_when_number_is_set(self):
        Profile.objects.create(full_name="M", headline="Dev")
        self.assertNotContains(self.client.get(reverse("portfolio:home")), "wa.me/")
        Profile.objects.update(whatsapp="+243 81 008 1623")
        self.assertContains(self.client.get(reverse("portfolio:home")), "https://wa.me/243810081623")

    def test_availability_badge(self):
        Profile.objects.create(full_name="M", headline="Dev", available_for_work=True)
        self.assertContains(self.client.get(reverse("portfolio:home")), "Disponible pour de nouvelles missions")
        Profile.objects.update(available_for_work=False)
        self.assertNotContains(self.client.get(reverse("portfolio:home")), "Disponible pour de nouvelles missions")

    def test_seed_demo_is_idempotent(self):
        call_command("seed_demo", stdout=StringIO())
        counts = (
            Profile.objects.count(),
            Project.objects.count(),
            Course.objects.count(),
            Service.objects.count(),
            FAQ.objects.count(),
            TimelineItem.objects.count(),
        )
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(
            counts,
            (
                Profile.objects.count(),
                Project.objects.count(),
                Course.objects.count(),
                Service.objects.count(),
                FAQ.objects.count(),
                TimelineItem.objects.count(),
            ),
        )
        self.assertGreater(Service.objects.count(), 0)
        self.assertEqual(self.client.get(reverse("portfolio:home")).status_code, 200)


class CybersecuritySectionTests(TestCase):
    def test_section_is_hidden_without_security_skills(self):
        Skill.objects.create(name="Python", category=Skill.Category.LANGUAGES, level=70)
        response = self.client.get(reverse("portfolio:home"))
        self.assertNotContains(response, 'id="cybersecurite"')
        self.assertEqual(response.context["security_skills"], [])

    def test_section_lists_security_skills_with_levels(self):
        Skill.objects.create(name="Sécurité des réseaux", category=Skill.Category.SECURITY, level=65)
        Skill.objects.create(name="Python", category=Skill.Category.LANGUAGES, level=70)
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, 'id="cybersecurite"')
        self.assertEqual([s.name for s in response.context["security_skills"]], ["Sécurité des réseaux"])
        self.assertContains(response, "securite.sh")

    def test_security_skills_feed_the_technology_marquee(self):
        Skill.objects.create(name="Sécurité web", category=Skill.Category.SECURITY, level=60)
        Skill.objects.create(name="Gestion de projet", category=Skill.Category.TOOLS, level=60)
        marquee = self.client.get(reverse("portfolio:home")).context["marquee_items"]
        self.assertIn("Sécurité web", marquee)
        self.assertNotIn("Gestion de projet", marquee)

    def test_security_category_comes_before_tools_in_skill_order(self):
        Skill.objects.create(name="Méthodes", category=Skill.Category.TOOLS, level=50)
        Skill.objects.create(name="Pare-feu", category=Skill.Category.SECURITY, level=50)
        Skill.objects.create(name="Réseau", category=Skill.Category.SYSTEMS, level=50)
        names = [s.name for s in self.client.get(reverse("portfolio:home")).context["skills"]]
        self.assertEqual(names, ["Réseau", "Pare-feu", "Méthodes"])

    def test_cybersecurity_service_can_use_the_shield_icon(self):
        Service.objects.create(title="Cybersécurité", description="d", icon=Service.Icon.SHIELD)
        self.assertContains(self.client.get(reverse("portfolio:home")), "Cybersécurité")


class HeroRolesTests(TestCase):
    def test_roles_list_parsing(self):
        profile = Profile(full_name="M", headline="Dev", roles=" Développeur web ,, Cybersécurité , Formateur ")
        self.assertEqual(profile.roles_list, ["Développeur web", "Cybersécurité", "Formateur"])
        self.assertEqual(Profile(full_name="M", headline="Dev").roles_list, [])

    def test_hero_exposes_roles_to_the_typewriter_with_noscript_fallback(self):
        Profile.objects.create(full_name="M", headline="Dev", roles="Développeur web, Cybersécurité")
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, 'data-typewriter="Développeur web|Cybersécurité"')
        # Le premier rôle est déjà dans le HTML : visible sans JavaScript.
        self.assertContains(response, ">Développeur web</span>")

    def test_hero_without_roles_shows_the_static_headline(self):
        Profile.objects.create(full_name="M", headline="Ingénieur logiciel")
        response = self.client.get(reverse("portfolio:home"))
        self.assertNotContains(response, "data-typewriter")
        self.assertContains(response, "Ingénieur logiciel")

    def test_role_text_is_escaped_in_the_attribute(self):
        Profile.objects.create(full_name="M", headline="Dev", roles='A"><script>x</script>, B')
        self.assertNotContains(self.client.get(reverse("portfolio:home")), "<script>x</script>")


class CommandPaletteTests(TestCase):
    def test_palette_is_rendered_on_every_page_with_navigation_targets(self):
        for url in (reverse("portfolio:home"), reverse("courses:list"), "/cette-page-nexiste-pas/"):
            response = self.client.get(url)
            self.assertContains(response, 'id="cmdk"', status_code=response.status_code)
            self.assertContains(response, "#cybersecurite", status_code=response.status_code)
            self.assertContains(response, "data-cmdk-open", status_code=response.status_code)

    def test_palette_shows_login_links_to_anonymous_and_account_links_when_logged_in(self):
        anonymous = self.client.get(reverse("portfolio:home")).content.decode()
        palette = anonymous[anonymous.index('id="cmdk"') :]
        self.assertIn(reverse("accounts:login"), palette)
        self.assertNotIn(reverse("courses:dashboard"), palette)

        User = get_user_model()
        self.client.force_login(User.objects.create_user("alice", "a@x.com", "pw"))
        logged = self.client.get(reverse("portfolio:home")).content.decode()
        palette = logged[logged.index('id="cmdk"') :]
        self.assertIn(reverse("courses:dashboard"), palette)

    def test_admin_link_only_for_staff(self):
        User = get_user_model()
        self.client.force_login(User.objects.create_user("alice", "a@x.com", "pw"))
        palette = self.client.get(reverse("portfolio:home")).content.decode()
        self.assertNotIn(reverse("admin:index"), palette[palette.index('id="cmdk"') :])
        self.client.force_login(User.objects.create_user("staff", "s@x.com", "pw", is_staff=True))
        palette = self.client.get(reverse("portfolio:home")).content.decode()
        self.assertIn(reverse("admin:index"), palette[palette.index('id="cmdk"') :])


class ProfileModelTests(TestCase):
    def test_social_links_and_digits(self):
        profile = Profile(
            full_name="Michel Kamango",
            headline="Dev",
            phone="+243 810 081 623",
            whatsapp="+243 (81) 008-1623",
            github_url="https://github.com/x",
            youtube_url="https://youtube.com/@x",
        )
        self.assertEqual(profile.initials, "MK")
        self.assertEqual(profile.phone_digits, "+243810081623")
        self.assertEqual(profile.whatsapp_digits, "243810081623")
        self.assertEqual([icon for icon, _label, _url in profile.social_links], ["github", "youtube"])


class SeoTests(TestCase):
    def test_robots_txt(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        body = response.content.decode()
        self.assertIn("Disallow: /admin/", body)
        self.assertIn("Disallow: /mon-espace/", body)
        self.assertIn("Sitemap: http://testserver/sitemap.xml", body)

    def test_sitemap_lists_pages_and_published_courses_only(self):
        visible = make_course(title="Indexé")
        make_course(title="Secret", is_published=False)
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("http://testserver/cours/", body)
        self.assertIn(f"http://testserver{visible.get_absolute_url()}", body)
        self.assertNotIn("secret", body)

    def test_home_has_canonical_open_graph_and_person_jsonld(self):
        Profile.objects.create(
            full_name="Michel Test", headline="Dev", email="m@example.com", github_url="https://github.com/m"
        )
        response = self.client.get(reverse("portfolio:home"))
        self.assertContains(response, '<link rel="canonical" href="http://testserver/">')
        self.assertContains(response, 'property="og:title"')
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S)
        data = json.loads(match.group(1))
        self.assertEqual(data["@type"], "Person")
        self.assertEqual(data["name"], "Michel Test")
        self.assertEqual(data["sameAs"], ["https://github.com/m"])

    def test_private_pages_are_noindex(self):
        User = get_user_model()
        self.client.force_login(User.objects.create_user("alice", "a@x.com", "pw"))
        for name in ("courses:dashboard", "accounts:profile"):
            self.assertContains(self.client.get(reverse(name)), 'content="noindex, nofollow"')

    def test_jsonld_cannot_break_out_of_script_tag(self):
        payload = jsonld({"name": "</script><script>alert(1)</script> & <b>"})
        self.assertNotIn("<", payload)
        self.assertNotIn(">", payload)
        self.assertEqual(json.loads(payload)["name"], "</script><script>alert(1)</script> & <b>")

    def test_healthz(self):
        response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertIn("no-cache", response["Cache-Control"])

    def test_404_page_uses_site_layout(self):
        response = self.client.get("/cette-page-nexiste-pas/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Cette page est introuvable", status_code=404)


class IconTagTests(TestCase):
    def render(self, template):
        return Template(template).render(Context({}))

    def test_known_icons_render_svg(self):
        stroke = self.render('{% icon "check" "h-4 w-4" %}')
        self.assertIn("<svg", stroke)
        self.assertIn('class="h-4 w-4"', stroke)
        self.assertIn('aria-hidden="true"', stroke)
        self.assertIn('fill="currentColor"', self.render('{% icon "github" %}'))

    def test_unknown_icon_renders_nothing(self):
        self.assertEqual(self.render('{% icon "nope" %}').strip(), "")

    def test_css_class_is_escaped(self):
        html = Template('{% icon "check" css %}').render(Context({"css": '"><script>x</script>'}))
        self.assertNotIn("<script>", html)

    def test_every_service_icon_choice_has_a_drawing(self):
        for value, _label in Service.Icon.choices:
            self.assertIn("<svg", self.render('{% icon "' + value + '" %}'), value)

    def test_every_icon_used_in_templates_exists(self):
        """Une faute de frappe dans {% icon "..." %} ne doit jamais passer inaperçue."""
        from pathlib import Path

        from django.conf import settings

        from .templatetags.ui import FILL_ICONS, STROKE_ICONS

        known = set(STROKE_ICONS) | set(FILL_ICONS)
        used = set()
        for path in Path(settings.BASE_DIR, "templates").rglob("*.html"):
            used.update(re.findall(r'\{% icon "([a-z-]+)"', path.read_text(encoding="utf-8")))
        self.assertTrue(used, "aucune icône trouvée : le test ne vérifie plus rien")
        self.assertEqual(used - known, set())


class CodeLinesFilterTests(TestCase):
    def render(self, value, width=30):
        return Template("{% for p in v|code_lines:w %}[{{ p }}]{% endfor %}").render(Context({"v": value, "w": width}))

    def test_short_text_stays_on_one_line(self):
        self.assertEqual(self.render("Développeur Python"), "[Développeur Python]")

    def test_long_text_is_split_at_word_boundaries_keeping_spaces(self):
        text = "Développeur d'applications & bases de données"
        # Le gabarit échappe l'HTML (apostrophe, &) : on le décode avant de comparer.
        rendered = html.unescape(self.render(text))
        chunks = rendered.strip("[]").split("][")
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk.rstrip()) <= 30 for chunk in chunks))
        # Concaténées, les parties redonnent exactement le texte d'origine.
        self.assertEqual("".join(chunks), text)

    def test_empty_value_gives_no_lines(self):
        self.assertEqual(self.render(""), "")
        self.assertEqual(self.render(None), "")


class ContactTests(TestCase):
    payload = {"name": "Alice", "email": "alice@example.com", "subject": "Bonjour", "message": "Un message"}

    def test_valid_message_is_saved(self):
        response = self.client.post(reverse("portfolio:contact"), self.payload)
        self.assertRedirects(response, f"{reverse('portfolio:home')}#contact", fetch_redirect_response=False)
        self.assertEqual(ContactMessage.objects.count(), 1)

    @override_settings(CONTACT_RECIPIENT="moi@example.com")
    def test_notification_email_is_sent(self):
        self.client.post(reverse("portfolio:contact"), self.payload)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["moi@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["alice@example.com"])

    def test_invalid_message_shows_errors_and_is_not_saved(self):
        response = self.client.post(reverse("portfolio:contact"), {**self.payload, "email": "pas-un-email"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_honeypot_silently_drops_spam(self):
        response = self.client.post(reverse("portfolio:contact"), {**self.payload, "website": "http://spam"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(reverse("portfolio:contact")).status_code, 405)


class PaymentSwitchTests(TestCase):
    def test_demo_banner_follows_the_simulated_switch(self):
        from unittest import mock

        User = get_user_model()
        course = make_course(price=Decimal("10"))
        self.client.force_login(User.objects.create_user("alice", "a@x.com", "pw"))
        url = reverse("courses:checkout", args=[course.slug])
        self.assertContains(self.client.get(url), "Mode démonstration")
        with mock.patch("courses.payments.SIMULATED", False):
            self.assertNotContains(self.client.get(url), "Mode démonstration")
