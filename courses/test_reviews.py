import json
import re
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Course, Order, Review

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


def buyer(name, course, **user_kwargs):
    user = User.objects.create_user(name, f"{name}@example.com", "pw-Str0ng!", **user_kwargs)
    Order.objects.create(user=user, course=course, amount=course.price, status=Order.Status.PAID)
    return user


class ReviewSubmissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = make_course()
        cls.buyer = buyer("alice", cls.course)
        cls.stranger = User.objects.create_user("bob", "bob@example.com", "pw-Str0ng!")
        cls.url = reverse("courses:review", args=[cls.course.slug])

    def test_requires_login(self):
        response = self.client.post(self.url, {"rating": 5})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])
        self.assertFalse(Review.objects.exists())

    def test_get_is_not_allowed(self):
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_buyer_can_publish_a_review(self):
        self.client.force_login(self.buyer)
        response = self.client.post(self.url, {"rating": 4, "comment": "Très clair !"})
        self.assertRedirects(response, f"{reverse('courses:access', args=[self.course.slug])}#avis")
        review = Review.objects.get()
        self.assertEqual((review.user, review.course, review.rating, review.comment), (self.buyer, self.course, 4, "Très clair !"))
        self.assertTrue(review.is_approved)

    def test_non_buyer_cannot_review(self):
        self.client.force_login(self.stranger)
        response = self.client.post(self.url, {"rating": 5, "comment": "Je n'ai pas acheté"})
        self.assertRedirects(response, self.course.get_absolute_url())
        self.assertFalse(Review.objects.exists())

    def test_superuser_who_never_bought_cannot_review(self):
        admin = User.objects.create_superuser("root", "root@example.com", "pw-Str0ng!")
        self.client.force_login(admin)
        self.client.post(self.url, {"rating": 5})
        self.assertFalse(Review.objects.exists())

    def test_pending_order_does_not_allow_a_review(self):
        other = make_course(title="Autre cours")
        user = User.objects.create_user("carl", "carl@example.com", "pw-Str0ng!")
        Order.objects.create(user=user, course=other, amount=5, status=Order.Status.PENDING)
        self.client.force_login(user)
        self.client.post(reverse("courses:review", args=[other.slug]), {"rating": 5})
        self.assertFalse(Review.objects.exists())

    def test_resubmitting_updates_the_same_review(self):
        self.client.force_login(self.buyer)
        self.client.post(self.url, {"rating": 3, "comment": "Bien"})
        self.client.post(self.url, {"rating": 5, "comment": "Finalement excellent"})
        review = Review.objects.get()
        self.assertEqual((review.rating, review.comment), (5, "Finalement excellent"))

    def test_invalid_ratings_are_rejected(self):
        self.client.force_login(self.buyer)
        for bad in ("0", "6", "-1", "abc", ""):
            response = self.client.post(self.url, {"rating": bad, "comment": "x"})
            self.assertEqual(response.status_code, 400, bad)
        self.assertFalse(Review.objects.exists())

    def test_overlong_comment_is_rejected(self):
        self.client.force_login(self.buyer)
        response = self.client.post(self.url, {"rating": 5, "comment": "x" * 1001})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Review.objects.exists())

    def test_user_and_course_cannot_be_forged_through_the_form(self):
        self.client.force_login(self.buyer)
        self.client.post(self.url, {"rating": 5, "user": self.stranger.pk, "course": 999, "is_approved": "", "id": 42})
        review = Review.objects.get()
        self.assertEqual((review.user, review.course), (self.buyer, self.course))
        self.assertTrue(review.is_approved)

    def test_one_review_per_user_and_course_is_enforced_by_the_database(self):
        Review.objects.create(course=self.course, user=self.buyer, rating=4)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(course=self.course, user=self.buyer, rating=5)

    def test_hidden_review_stays_hidden_after_the_author_edits_it(self):
        self.client.force_login(self.buyer)
        self.client.post(self.url, {"rating": 1, "comment": "Contenu inapproprié"})
        Review.objects.update(is_approved=False)  # modération
        self.client.post(self.url, {"rating": 1, "comment": "Toujours inapproprié"})
        self.assertFalse(Review.objects.get().is_approved)

    def test_review_form_is_only_shown_to_buyers_on_the_access_page(self):
        self.client.force_login(self.buyer)
        self.assertContains(self.client.get(reverse("courses:access", args=[self.course.slug])), 'name="rating"')
        admin = User.objects.create_superuser("root", "root@example.com", "pw-Str0ng!")
        self.client.force_login(admin)  # accès en aperçu, mais pas acheteur
        self.assertNotContains(self.client.get(reverse("courses:access", args=[self.course.slug])), 'name="rating"')

    def test_existing_review_is_prefilled(self):
        Review.objects.create(course=self.course, user=self.buyer, rating=4, comment="Mon avis initial")
        self.client.force_login(self.buyer)
        response = self.client.get(reverse("courses:access", args=[self.course.slug]))
        self.assertContains(response, "Mon avis initial")
        self.assertRegex(response.content.decode(), r'id="star4"[^>]*checked')
        self.assertContains(response, "Mettre à jour mon avis")


class ReviewDisplayTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = make_course()
        cls.alice = buyer("alice", cls.course, first_name="Alice", last_name="Martin")
        cls.bob = buyer("bob", cls.course)
        cls.carl = buyer("carl", cls.course)
        Review.objects.create(course=cls.course, user=cls.alice, rating=5, comment="Excellent !")
        Review.objects.create(course=cls.course, user=cls.bob, rating=4, comment="Très bien")
        Review.objects.create(course=cls.course, user=cls.carl, rating=1, comment="Avis masqué", is_approved=False)

    def test_with_ratings_counts_only_approved_reviews(self):
        course = Course.objects.with_ratings().get(pk=self.course.pk)
        self.assertEqual(course.rating_count, 2)
        self.assertAlmostEqual(course.avg_rating, 4.5)

    def test_course_without_reviews_has_no_rating(self):
        empty = make_course(title="Sans avis")
        course = Course.objects.with_ratings().get(pk=empty.pk)
        self.assertEqual(course.rating_count, 0)
        self.assertIsNone(course.avg_rating)

    def test_detail_page_shows_summary_and_approved_reviews_only(self):
        response = self.client.get(self.course.get_absolute_url())
        self.assertContains(response, "Excellent !")
        self.assertContains(response, "Très bien")
        self.assertNotContains(response, "Avis masqué")
        self.assertEqual(response.context["rating"]["count"], 2)
        self.assertEqual(response.context["rating"]["avg"], 4.5)
        bars = {bar["stars"]: bar["n"] for bar in response.context["rating"]["bars"]}
        self.assertEqual(bars, {5: 1, 4: 1, 3: 0, 2: 0, 1: 0})  # l'avis masqué (1 étoile) n'est pas compté

    def test_reviewer_names_never_leak_emails(self):
        response = self.client.get(self.course.get_absolute_url())
        self.assertContains(response, "Alice M.")
        self.assertContains(response, ">bob<")  # sans prénom : nom d'utilisateur
        self.assertNotContains(response, "alice@example.com")
        self.assertNotContains(response, "bob@example.com")

    def test_author_name_variants(self):
        user = User(username="zed", first_name="Zoé", last_name="")
        self.assertEqual(Review(user=user).author_name, "Zoé")
        self.assertEqual(Review(user=User(username="zed")).author_name, "zed")

    def test_cards_show_the_average_in_the_catalogue(self):
        response = self.client.get(reverse("courses:list"))
        self.assertContains(response, "(2 avis)")
        self.assertContains(response, "4,5")  # séparateur décimal français

    def test_cards_without_reviews_show_no_rating_line(self):
        Review.objects.all().delete()
        self.assertNotContains(self.client.get(reverse("courses:list")), "avis)")

    def test_structured_data_only_contains_real_ratings(self):
        def jsonld(response):
            return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S).group(1))

        rating = jsonld(self.client.get(self.course.get_absolute_url()))["aggregateRating"]
        self.assertEqual((rating["ratingValue"], rating["reviewCount"]), (4.5, 2))

        empty = make_course(title="Sans avis")
        self.assertNotIn("aggregateRating", jsonld(self.client.get(empty.get_absolute_url())))

    def test_home_shows_ratings_on_course_cards(self):
        self.assertContains(self.client.get(reverse("portfolio:home")), "(2 avis)")

    def test_empty_state_message(self):
        empty = make_course(title="Sans avis")
        self.assertContains(self.client.get(empty.get_absolute_url()), "Pas encore d'avis")
