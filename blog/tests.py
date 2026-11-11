import json
import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from portfolio.models import Profile

from .models import Post
from .templatetags.blog_tags import markdown_safe

User = get_user_model()


def make_post(**kwargs):
    defaults = {"title": "Un article", "excerpt": "Résumé", "content": "Contenu **gras**."}
    defaults.update(kwargs)
    return Post.objects.create(**defaults)


class PostModelTests(TestCase):
    def test_slug_is_generated_and_unique(self):
        self.assertEqual(make_post(title="Mon article").slug, "mon-article")
        self.assertEqual(make_post(title="Mon article").slug, "mon-article-2")

    def test_reading_time_has_a_minimum_of_one_minute(self):
        self.assertEqual(make_post(content="Court").reading_time, 1)
        self.assertEqual(make_post(title="Long", content="mot " * 650).reading_time, 4)  # 650 mots / 200 par minute

    def test_tag_list(self):
        self.assertEqual(make_post(tags=" Cybersécurité ,, Django , ").tag_list, ["Cybersécurité", "Django"])

    def test_published_manager_hides_drafts_and_future_posts(self):
        live = make_post(title="Visible")
        make_post(title="Brouillon", is_published=False)
        make_post(title="Programmé", published_at=timezone.now() + timedelta(days=3))
        self.assertEqual(list(Post.objects.published()), [live])

    def test_is_live(self):
        self.assertTrue(make_post(title="A").is_live)
        self.assertFalse(make_post(title="B", is_published=False).is_live)
        self.assertFalse(make_post(title="C", published_at=timezone.now() + timedelta(days=1)).is_live)


class MarkdownSafetyTests(TestCase):
    """Le contenu vient de l'admin, mais on ne lui fait JAMAIS confiance : tout est nettoyé."""

    def test_formatting_is_rendered(self):
        html = markdown_safe("## Titre\n\nUn **gras**, un *italique* et du `code`.\n\n- a\n- b")
        self.assertIn("<h2", html)
        self.assertIn("<strong>gras</strong>", html)
        self.assertIn("<em>italique</em>", html)
        self.assertIn("<code>code</code>", html)
        self.assertIn("<li>a</li>", html)

    def test_headings_get_anchor_ids(self):
        self.assertRegex(markdown_safe("## Mon titre"), r'<h2 id="mon-titre">')

    def test_script_tags_are_removed(self):
        html = markdown_safe("Avant <script>alert(1)</script> après")
        self.assertNotIn("<script", html)
        self.assertNotIn("alert(1)", html)

    def test_event_handlers_and_styles_are_removed(self):
        html = markdown_safe('<img src="x.png" onerror="alert(1)" style="x"> <a href="https://a.fr" onclick="evil()">lien</a>')
        self.assertNotIn("onerror", html)
        self.assertNotIn("onclick", html)
        self.assertNotIn("style=", html)
        self.assertIn('src="x.png"', html)

    def test_dangerous_link_schemes_are_removed(self):
        html = markdown_safe("[clic](javascript:alert(1)) et [mail](mailto:a@b.fr) et [ok](https://exemple.fr)")
        self.assertNotIn("javascript:", html)
        self.assertIn("mailto:a@b.fr", html)
        self.assertIn('href="https://exemple.fr"', html)

    def test_iframes_and_forms_are_removed(self):
        html = markdown_safe('<iframe src="https://evil.example"></iframe><form action="/x"><input></form>')
        for tag in ("<iframe", "<form", "<input"):
            self.assertNotIn(tag, html)

    def test_external_links_get_noopener(self):
        self.assertIn("noopener noreferrer", markdown_safe("[x](https://exemple.fr)"))

    def test_filter_is_usable_in_templates_and_marks_output_safe(self):
        out = Template("{% load blog_tags %}{{ t|markdown_safe }}").render(Context({"t": "**ok**"}))
        self.assertIn("<strong>ok</strong>", out)

    def test_empty_content(self):
        self.assertEqual(str(markdown_safe("")).strip(), "")
        self.assertEqual(str(markdown_safe(None)).strip(), "")


class PostListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("blog:list")

    def test_empty_blog_renders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun article")

    def test_only_published_posts_are_listed(self):
        make_post(title="Visible")
        make_post(title="Brouillon", is_published=False)
        make_post(title="Programmé", published_at=timezone.now() + timedelta(days=2))
        response = self.client.get(self.url)
        self.assertContains(response, "Visible")
        self.assertNotContains(response, "Brouillon")
        self.assertNotContains(response, "Programmé")

    def test_search(self):
        make_post(title="Mots de passe", content="Les mots de passe solides")
        make_post(title="Wi-Fi", content="Réseau sans fil")
        titles = [p.title for p in self.client.get(self.url, {"q": "solides"}).context["posts"]]
        self.assertEqual(titles, ["Mots de passe"])

    def test_tag_filter_is_case_insensitive_and_exact(self):
        make_post(title="A", tags="Cybersécurité, Réseaux")
        make_post(title="B", tags="Django")
        make_post(title="C", tags="Cybersécurité avancée")  # contient le mot mais n'est PAS ce tag
        titles = [p.title for p in self.client.get(self.url, {"tag": "cybersécurité"}).context["posts"]]
        self.assertEqual(titles, ["A"])

    def test_tag_cloud_counts_published_posts_only(self):
        make_post(title="A", tags="Cybersécurité")
        make_post(title="B", tags="Cybersécurité, Django")
        make_post(title="C", tags="Secret", is_published=False)
        tags = dict(self.client.get(self.url).context["tags"])
        self.assertEqual(tags, {"Cybersécurité": 2, "Django": 1})

    def test_featured_post_is_highlighted_only_on_unfiltered_first_page(self):
        star = make_post(title="Vedette", is_featured=True, tags="X")
        self.assertEqual(self.client.get(self.url).context["featured"], star)
        self.assertEqual([p.title for p in self.client.get(self.url).context["posts"]], [])  # pas de doublon
        self.assertIsNone(self.client.get(self.url, {"q": "Vedette"}).context["featured"])
        self.assertIsNone(self.client.get(self.url, {"tag": "X"}).context["featured"])

    def test_pagination(self):
        for i in range(8):
            make_post(title=f"Article {i}")
        self.assertEqual(len(self.client.get(self.url).context["posts"]), 6)
        self.assertEqual(len(self.client.get(self.url, {"page": 2}).context["posts"]), 2)
        self.assertEqual(self.client.get(self.url, {"page": "abc"}).status_code, 200)

    def test_search_term_is_escaped(self):
        self.assertNotContains(self.client.get(self.url, {"q": "<script>alert(1)</script>"}), "<script>alert(1)</script>")


class PostDetailTests(TestCase):
    def test_published_post_is_public_with_seo_data(self):
        Profile.objects.create(full_name="Michel Test", headline="Dev")
        post = make_post(title="Sécurité", excerpt="Le résumé", tags="Cybersécurité")
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Le résumé")
        self.assertContains(response, 'content="index, follow"')
        self.assertContains(response, 'property="og:type" content="article"')
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S)
        data = json.loads(match.group(1))
        self.assertEqual(data["@type"], "BlogPosting")
        self.assertEqual(data["headline"], "Sécurité")
        self.assertEqual(data["author"]["name"], "Michel Test")

    def test_content_is_sanitised_on_the_page(self):
        post = make_post(content="Texte <script>alert('xss')</script> **sûr**")
        response = self.client.get(post.get_absolute_url())
        self.assertNotContains(response, "<script>alert('xss')")
        self.assertContains(response, "<strong>sûr</strong>")

    def test_draft_is_404_for_the_public(self):
        draft = make_post(title="Brouillon", is_published=False)
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)

    def test_scheduled_post_is_404_for_the_public(self):
        future = make_post(title="Futur", published_at=timezone.now() + timedelta(days=5))
        self.assertEqual(self.client.get(future.get_absolute_url()).status_code, 404)

    def test_staff_can_preview_a_draft_which_is_noindex(self):
        draft = make_post(title="Brouillon", is_published=False)
        self.client.force_login(User.objects.create_user("staff", "s@x.com", "pw", is_staff=True))
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aperçu réservé à l'administration")
        self.assertContains(response, 'content="noindex, nofollow"')

    def test_regular_user_cannot_preview_a_draft(self):
        draft = make_post(title="Brouillon", is_published=False)
        self.client.force_login(User.objects.create_user("alice", "a@x.com", "pw"))
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)

    def test_related_posts_prefer_shared_tags(self):
        base = make_post(title="Base", tags="Cybersécurité, Réseaux")
        close = make_post(title="Proche", tags="Réseaux", published_at=timezone.now() - timedelta(days=30))
        recent = make_post(title="Récent sans lien", tags="Cuisine")
        related = self.client.get(base.get_absolute_url()).context["related_posts"]
        self.assertEqual([p.title for p in related], [close.title, recent.title])
        self.assertNotIn(base, related)

    def test_previous_and_next_posts(self):
        now = timezone.now()
        old = make_post(title="Ancien", published_at=now - timedelta(days=10))
        mid = make_post(title="Milieu", published_at=now - timedelta(days=5))
        new = make_post(title="Nouveau", published_at=now - timedelta(days=1))
        context = self.client.get(mid.get_absolute_url()).context
        self.assertEqual(context["previous_post"], old)
        self.assertEqual(context["next_post"], new)
        self.assertIsNone(self.client.get(new.get_absolute_url()).context["next_post"])


class FeedAndSitemapTests(TestCase):
    def test_rss_feed_lists_only_published_posts(self):
        Profile.objects.create(full_name="Michel Test", headline="Dev")
        make_post(title="Dans le flux", excerpt="Résumé RSS", tags="Cybersécurité")
        make_post(title="Pas dans le flux", is_published=False)
        response = self.client.get(reverse("blog:rss"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response["Content-Type"])
        body = response.content.decode()
        self.assertIn("Dans le flux", body)
        self.assertIn("Résumé RSS", body)
        self.assertNotIn("Pas dans le flux", body)
        self.assertIn("Blog — Michel Test", body)

    def test_rss_feed_is_advertised_in_every_page(self):
        self.assertContains(self.client.get("/"), 'type="application/rss+xml"')

    def test_sitemap_lists_posts_and_new_pages(self):
        visible = make_post(title="Indexé")
        make_post(title="Caché", is_published=False)
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertIn(f"http://testserver{visible.get_absolute_url()}", body)
        self.assertNotIn("/blog/cache/", body)
        for path in ("/blog/", "/cv/", "/securite/"):
            self.assertIn(f"http://testserver{path}", body)
