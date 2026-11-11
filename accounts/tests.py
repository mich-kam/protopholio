import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

GOOD_PASSWORD = "Mot-de-passe-S0lide!"


class RegistrationTests(TestCase):
    def test_register_logs_the_user_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {"username": "alice", "email": "alice@example.com", "password1": GOOD_PASSWORD, "password2": GOOD_PASSWORD},
        )
        self.assertRedirects(response, reverse("courses:dashboard"))
        self.assertTrue(User.objects.filter(username="alice").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get().pk)

    def test_register_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user("bob", "Bob@Example.com", "pw-Str0ng!")
        response = self.client.post(
            reverse("accounts:register"),
            {"username": "bob2", "email": "bob@example.com", "password1": GOOD_PASSWORD, "password2": GOOD_PASSWORD},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "existe déjà")
        self.assertFalse(User.objects.filter(username="bob2").exists())

    def test_register_ignores_open_redirect(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "eve",
                "email": "eve@example.com",
                "password1": GOOD_PASSWORD,
                "password2": GOOD_PASSWORD,
                "next": "https://evil.example.org/",
            },
        )
        self.assertRedirects(response, reverse("courses:dashboard"))


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("alice", "Alice@Example.com", GOOD_PASSWORD)

    def login(self, identifier, password=GOOD_PASSWORD):
        return self.client.post(reverse("accounts:login"), {"username": identifier, "password": password})

    def test_login_with_username(self):
        self.assertRedirects(self.login("alice"), reverse("courses:dashboard"))

    def test_login_with_email_case_insensitively(self):
        self.assertRedirects(self.login("alice@example.COM"), reverse("courses:dashboard"))

    def test_username_is_case_insensitive(self):
        self.assertRedirects(self.login("ALICE"), reverse("courses:dashboard"))

    def test_wrong_password_is_refused(self):
        response = self.login("alice", "mauvais")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unknown_account_is_refused(self):
        response = self.login("inconnu@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save()
        self.assertEqual(self.login("alice").status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_and_logout(self):
        self.login("alice")
        # La déconnexion se fait en POST uniquement.
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("portfolio:home"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("alice", "alice@example.com", GOOD_PASSWORD)
        cls.other = User.objects.create_user("bob", "bob@example.com", GOOD_PASSWORD)

    def test_profile_requires_login(self):
        url = reverse("accounts:profile")
        self.assertRedirects(self.client.get(url), f"{reverse('accounts:login')}?next={url}")

    def test_update_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accounts:profile"),
            {"first_name": "Alice", "last_name": "Martin", "email": "alice.martin@example.com"},
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertEqual((self.user.first_name, self.user.email), ("Alice", "alice.martin@example.com"))

    def test_cannot_take_another_users_email(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accounts:profile"), {"first_name": "", "last_name": "", "email": "BOB@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "déjà utilisée")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "alice@example.com")

    def test_can_keep_own_email(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accounts:profile"), {"first_name": "A", "last_name": "B", "email": "alice@example.com"}
        )
        self.assertRedirects(response, reverse("accounts:profile"))

    def test_password_change_keeps_user_logged_in(self):
        self.client.force_login(self.user)
        new_password = "Autre-Mot-de-passe-9!"
        response = self.client.post(
            reverse("accounts:password_change"),
            {"old_password": GOOD_PASSWORD, "new_password1": new_password, "new_password2": new_password},
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 200)

    def test_password_change_rejects_wrong_old_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("accounts:password_change"),
            {"old_password": "faux", "new_password1": "Zzz-9988-xyz!", "new_password2": "Zzz-9988-xyz!"},
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(GOOD_PASSWORD))


class PasswordResetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("alice", "alice@example.com", GOOD_PASSWORD)

    def test_full_reset_flow(self):
        response = self.client.post(reverse("accounts:password_reset"), {"email": "ALICE@example.com"})
        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["alice@example.com"])

        link = re.search(r"https?://testserver(/comptes/mot-de-passe/reinitialiser/\S+)", mail.outbox[0].body)
        self.assertIsNotNone(link, mail.outbox[0].body)

        # Django remplace le jeton de l'URL par un jeton de session avant d'afficher le formulaire.
        response = self.client.get(link.group(1), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["validlink"])
        form_url = response.redirect_chain[-1][0]

        new_password = "Nouveau-Mot-de-passe-7!"
        response = self.client.post(form_url, {"new_password1": new_password, "new_password2": new_password})
        self.assertRedirects(response, reverse("accounts:password_reset_complete"))

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertTrue(self.client.login(username="alice", password=new_password))

    def test_unknown_email_gives_same_response_and_sends_nothing(self):
        response = self.client.post(reverse("accounts:password_reset"), {"email": "inconnu@example.com"})
        # Même réponse que pour un vrai compte : impossible de deviner quelles adresses existent.
        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_token_is_rejected(self):
        url = reverse("accounts:password_reset_confirm", args=["MQ", "invalide-jeton"])
        response = self.client.get(url, follow=True)
        self.assertFalse(response.context["validlink"])
        self.assertContains(response, "Lien invalide")
