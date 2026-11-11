import shutil
import tempfile
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from .admin import _csv_safe
from .models import Course, Order

User = get_user_model()


def make_course(**kwargs):
    defaults = {
        "title": "Python pour débutants",
        "short_description": "Résumé",
        "description": "Description",
        "price": Decimal("15.00"),
        "course_url": "https://example.com/cours",
    }
    defaults.update(kwargs)
    return Course.objects.create(**defaults)


def make_user(name="alice", **kwargs):
    return User.objects.create_user(name, f"{name}@example.com", "pw-Str0ng!", **kwargs)


class CourseModelTests(TestCase):
    def test_slug_is_generated_and_unique(self):
        a = make_course(title="Mon cours")
        b = make_course(title="Mon cours")
        self.assertEqual(a.slug, "mon-cours")
        self.assertEqual(b.slug, "mon-cours-2")

    def test_published_manager(self):
        make_course(title="Visible")
        make_course(title="Brouillon", is_published=False)
        self.assertEqual(list(Course.objects.published().values_list("title", flat=True)), ["Visible"])

    def test_cannot_have_two_paid_orders_for_same_course(self):
        user = make_user()
        course = make_course()
        Order.objects.create(user=user, course=course, amount=course.price, status=Order.Status.PAID)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.create(user=user, course=course, amount=course.price, status=Order.Status.PAID)

    def test_bullet_lists_are_parsed_from_text(self):
        course = make_course(
            learning_outcomes="Premier point\n- Deuxième point\n\n• Troisième point\n",
            requirements="  Un ordinateur  ",
        )
        self.assertEqual(course.outcomes_list, ["Premier point", "Deuxième point", "Troisième point"])
        self.assertEqual(course.requirements_list, ["Un ordinateur"])
        self.assertEqual(make_course(title="Vide").outcomes_list, [])

    def test_featured_courses_come_first(self):
        make_course(title="Ancien", is_featured=True)
        make_course(title="Récent")
        self.assertEqual(Course.objects.first().title, "Ancien")

    def test_is_new_only_for_recent_courses(self):
        course = make_course()
        self.assertTrue(course.is_new)
        Course.objects.filter(pk=course.pk).update(created_at=course.created_at.replace(year=2020))
        course.refresh_from_db()
        self.assertFalse(course.is_new)


class CatalogueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.py = make_course(title="Python avancé", level=Course.Level.ADVANCED, price=Decimal("30"))
        cls.html = make_course(
            title="HTML gratuit", level=Course.Level.BEGINNER, price=Decimal("0"), short_description="Web"
        )
        cls.sql = make_course(title="SQL", level=Course.Level.INTERMEDIATE, price=Decimal("10"))
        cls.url = reverse("courses:list")

    def titles(self, response):
        return [c.title for c in response.context["courses"]]

    def test_search_matches_title_and_description(self):
        self.assertEqual(self.titles(self.client.get(self.url, {"q": "python"})), ["Python avancé"])
        self.assertEqual(self.titles(self.client.get(self.url, {"q": "web"})), ["HTML gratuit"])
        self.assertEqual(self.titles(self.client.get(self.url, {"q": "introuvable"})), [])

    def test_level_and_price_filters(self):
        self.assertEqual(self.titles(self.client.get(self.url, {"niveau": "advanced"})), ["Python avancé"])
        self.assertEqual(self.titles(self.client.get(self.url, {"prix": "free"})), ["HTML gratuit"])
        paid = self.titles(self.client.get(self.url, {"prix": "paid"}))
        self.assertCountEqual(paid, ["Python avancé", "SQL"])

    def test_sorting_by_price(self):
        asc = self.titles(self.client.get(self.url, {"tri": "price_asc"}))
        self.assertEqual(asc, ["HTML gratuit", "SQL", "Python avancé"])
        desc = self.titles(self.client.get(self.url, {"tri": "price_desc"}))
        self.assertEqual(desc, ["Python avancé", "SQL", "HTML gratuit"])

    def test_invalid_parameters_are_ignored(self):
        response = self.client.get(self.url, {"niveau": "nope", "prix": "x", "tri": "drop table", "page": "abc"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total"], 3)
        self.assertFalse(response.context["has_filters"])

    def test_pagination(self):
        for i in range(10):
            make_course(title=f"Extra {i}")
        first = self.client.get(self.url)
        self.assertEqual(len(first.context["courses"]), 9)
        self.assertTrue(first.context["page_obj"].has_next())
        second = self.client.get(self.url, {"page": 2})
        self.assertEqual(len(second.context["courses"]), 4)

    def test_search_term_is_escaped(self):
        response = self.client.get(self.url, {"q": "<script>alert(1)</script>"})
        self.assertNotContains(response, "<script>alert(1)</script>")


class PurchaseFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_user("alice")
        cls.other = make_user("bob")
        cls.course = make_course()

    def test_public_pages(self):
        self.assertEqual(self.client.get(reverse("courses:list")).status_code, 200)
        self.assertEqual(self.client.get(self.course.get_absolute_url()).status_code, 200)

    def test_detail_shows_outcomes_related_courses_and_jsonld(self):
        course = make_course(title="Détaillé", learning_outcomes="Savoir A\nSavoir B", requirements="Prérequis X")
        make_course(title="Cours voisin")
        response = self.client.get(course.get_absolute_url())
        self.assertContains(response, "Savoir A")
        self.assertContains(response, "Prérequis X")
        self.assertContains(response, "Cours voisin")
        self.assertContains(response, '"@type":"Course"')
        self.assertNotIn(course, response.context["related_courses"])

    def test_unpublished_course_is_404(self):
        draft = make_course(title="Brouillon", is_published=False)
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)

    def test_dashboard_requires_login(self):
        url = reverse("courses:dashboard")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_checkout_requires_login(self):
        url = reverse("courses:checkout", args=[self.course.slug])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(url, {"payment_method": "card"}).status_code, 302)
        self.assertFalse(Order.objects.exists())

    def test_successful_purchase_sends_confirmation_email(self):
        self.client.force_login(self.user)
        url = reverse("courses:checkout", args=[self.course.slug])
        self.assertEqual(self.client.get(url).status_code, 200)

        response = self.client.post(url, {"payment_method": Order.PaymentMethod.CARD})
        self.assertRedirects(response, reverse("courses:access", args=[self.course.slug]))

        order = Order.objects.get()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(order.amount, Decimal("15.00"))
        self.assertIsNotNone(order.paid_at)
        self.assertTrue(self.course.is_accessible_by(self.user))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["alice@example.com"])
        self.assertIn(order.short_reference, mail.outbox[0].subject)
        self.assertIn(reverse("courses:receipt", args=[order.reference]), mail.outbox[0].body)

    def test_purchase_survives_email_failure(self):
        self.client.force_login(self.user)
        with mock.patch("courses.emails.send_mail", side_effect=OSError("smtp down")):
            response = self.client.post(
                reverse("courses:checkout", args=[self.course.slug]), {"payment_method": "card"}
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.get().status, Order.Status.PAID)

    def test_invalid_payment_method_does_not_create_paid_order(self):
        self.client.force_login(self.user)
        url = reverse("courses:checkout", args=[self.course.slug])
        response = self.client.post(url, {"payment_method": "bitcoin"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.filter(status=Order.Status.PAID).exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_double_purchase_is_prevented(self):
        self.client.force_login(self.user)
        url = reverse("courses:checkout", args=[self.course.slug])
        self.client.post(url, {"payment_method": "card"})
        response = self.client.post(url, {"payment_method": "card"})
        self.assertRedirects(response, reverse("courses:access", args=[self.course.slug]))
        self.assertEqual(Order.objects.filter(status=Order.Status.PAID).count(), 1)

    def test_free_course_needs_no_payment_method(self):
        free = make_course(title="Gratuit", price=Decimal("0"))
        self.client.force_login(self.user)
        self.client.post(reverse("courses:checkout", args=[free.slug]))
        order = Order.objects.get()
        self.assertEqual(order.payment_method, Order.PaymentMethod.FREE)
        self.assertEqual(order.status, Order.Status.PAID)

    def test_access_is_denied_without_purchase(self):
        self.client.force_login(self.other)
        url = reverse("courses:access", args=[self.course.slug])
        self.assertRedirects(self.client.get(url), self.course.get_absolute_url())

    def test_dashboard_lists_only_own_paid_courses(self):
        Order.objects.create(user=self.user, course=self.course, amount=15, status=Order.Status.PAID)
        pending = make_course(title="En attente")
        Order.objects.create(user=self.user, course=pending, amount=15, status=Order.Status.PENDING)

        self.client.force_login(self.user)
        response = self.client.get(reverse("courses:dashboard"))
        self.assertContains(response, "Python pour débutants")
        # Une commande non payée n'est jamais listée parmi les cours achetés...
        self.assertEqual([o.course.title for o in response.context["orders"]], ["Python pour débutants"])
        # ... mais le cours peut être suggéré dans les recommandations.
        self.assertEqual([c.title for c in response.context["recommended"]], ["En attente"])

        self.client.force_login(self.other)
        response = self.client.get(reverse("courses:dashboard"))
        self.assertEqual(response.context["orders"], [])

    def test_dashboard_totals(self):
        second = make_course(title="Deuxième", price=Decimal("5.50"))
        Order.objects.create(user=self.user, course=self.course, amount=Decimal("15"), status="paid")
        Order.objects.create(user=self.user, course=second, amount=Decimal("5.50"), status="paid")
        self.client.force_login(self.user)
        response = self.client.get(reverse("courses:dashboard"))
        self.assertEqual(response.context["total_spent"], Decimal("20.50"))

    def test_purchased_course_stays_accessible_after_unpublishing(self):
        Order.objects.create(user=self.user, course=self.course, amount=15, status=Order.Status.PAID)
        self.course.is_published = False
        self.course.save()
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("courses:access", args=[self.course.slug])).status_code, 200)

    def test_owned_courses_are_flagged_in_catalogue(self):
        Order.objects.create(user=self.user, course=self.course, amount=15, status=Order.Status.PAID)
        self.client.force_login(self.user)
        response = self.client.get(reverse("courses:list"))
        self.assertIn(self.course.pk, response.context["owned_ids"])
        self.assertContains(response, "Acquis")


class ReceiptTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_user("alice")
        cls.other = make_user("bob")
        cls.admin = User.objects.create_superuser("root", "root@example.com", "pw-Str0ng!")
        cls.course = make_course()
        cls.order = Order.objects.create(
            user=cls.user, course=cls.course, amount=15, status=Order.Status.PAID, payment_method="card"
        )
        cls.url = reverse("courses:receipt", args=[cls.order.reference])

    def test_owner_can_view_receipt(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, self.order.short_reference)
        self.assertContains(response, "Python pour débutants")
        self.assertContains(response, "mode démonstration")

    def test_other_user_gets_404(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_anonymous_is_redirected_to_login(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_superuser_can_view_any_receipt(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_unpaid_order_has_no_receipt(self):
        pending = Order.objects.create(user=self.user, course=make_course(title="Autre"), amount=5, status="pending")
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("courses:receipt", args=[pending.reference])).status_code, 404)

    def test_free_order_has_no_demo_notice(self):
        free = Order.objects.create(
            user=self.user, course=make_course(title="Gratuit", price=0), amount=0, status="paid", payment_method="free"
        )
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get(reverse("courses:receipt", args=[free.reference])), "mode démonstration")


class AdminExportTests(TestCase):
    def test_csv_safe_neutralises_formulas(self):
        for dangerous in ("=1+1", "+cmd", "-2", "@SUM(A1)"):
            self.assertTrue(_csv_safe(dangerous).startswith("'"))
        self.assertEqual(_csv_safe("Normal"), "Normal")
        self.assertEqual(_csv_safe(None), "")

    def test_export_action_outputs_escaped_csv(self):
        admin = User.objects.create_superuser("root", "root@example.com", "pw-Str0ng!")
        buyer = make_user("=cmd")
        order = Order.objects.create(user=buyer, course=make_course(), amount=15, status="paid")
        self.client.force_login(admin)
        response = self.client.post(
            reverse("admin:courses_order_changelist"),
            {"action": "export_csv", "_selected_action": [order.pk]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        body = response.content.decode("utf-8")
        self.assertIn("'=cmd", body)
        self.assertNotIn(";=cmd", body)


class ProtectedDownloadTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)

        self.user = make_user("alice")
        self.other = make_user("bob")
        self.course = make_course(
            course_url="",
            course_file=SimpleUploadedFile("cours.pdf", b"%PDF-1.4 contenu secret"),
        )
        Order.objects.create(user=self.user, course=self.course, amount=15, status=Order.Status.PAID)

    def test_buyer_can_download(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("courses:download", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"%PDF-1.4 contenu secret")
        self.assertIn("attachment", response["Content-Disposition"])

    def test_non_buyer_cannot_download(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("courses:download", args=[self.course.slug]))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_cannot_download(self):
        response = self.client.get(reverse("courses:download", args=[self.course.slug]))
        self.assertEqual(response.status_code, 302)

    def test_private_file_is_not_served_publicly_through_media(self):
        response = self.client.get(f"/media/{self.course.course_file.name}")
        self.assertEqual(response.status_code, 404)
