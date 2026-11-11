from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import throttle
from .models import FailedLogin

User = get_user_model()
PASSWORD = "Mot-de-passe-S0lide!"


class LoginThrottleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user("alice", "alice@example.com", PASSWORD)
        cls.bob = User.objects.create_user("bob", "bob@example.com", PASSWORD)
        cls.url = reverse("accounts:login")

    def attempt(self, identifier="alice", password="mauvais"):
        return self.client.post(self.url, {"username": identifier, "password": password})

    def fail(self, identifier="alice", times=1):
        for _ in range(times):
            self.attempt(identifier)

    def is_logged_in(self):
        return "_auth_user_id" in self.client.session

    def test_account_is_locked_after_five_failures_even_with_the_right_password(self):
        self.fail(times=5)
        response = self.attempt(password=PASSWORD)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.is_logged_in())
        self.assertContains(response, "Trop de tentatives échouées")

    def test_four_failures_do_not_lock(self):
        self.fail(times=4)
        self.assertRedirects(self.attempt(password=PASSWORD), reverse("courses:dashboard"))

    def test_successful_login_resets_the_counter(self):
        self.fail(times=4)
        self.attempt(password=PASSWORD)
        self.client.post(reverse("accounts:logout"))
        self.assertFalse(FailedLogin.objects.exists())
        self.fail(times=4)  # repart de zéro : toujours pas bloqué
        self.assertRedirects(self.attempt(password=PASSWORD), reverse("courses:dashboard"))

    def test_other_accounts_are_not_affected(self):
        self.fail("alice", times=5)
        self.assertRedirects(self.attempt("bob", PASSWORD), reverse("courses:dashboard"))

    def test_identifier_is_case_insensitive(self):
        self.fail("ALICE", times=3)
        self.fail("alice", times=2)
        self.assertTrue(throttle.is_locked("Alice"))

    def test_lock_expires_after_the_window(self):
        self.fail(times=5)
        self.assertTrue(throttle.is_locked("alice"))
        FailedLogin.objects.update(created_at=timezone.now() - throttle.WINDOW - timedelta(minutes=1))
        self.assertFalse(throttle.is_locked("alice"))
        self.assertRedirects(self.attempt(password=PASSWORD), reverse("courses:dashboard"))

    def test_blocked_attempts_do_not_extend_the_lock(self):
        self.fail(times=5)
        self.fail(times=4)  # tentatives pendant le blocage
        self.assertEqual(FailedLogin.objects.count(), throttle.MAX_FAILURES)

    def test_unknown_accounts_are_throttled_identically(self):
        """Impossible de distinguer un compte inexistant d'un compte réel grâce au blocage."""
        self.fail("fantome", times=5)
        self.assertContains(self.attempt("fantome", "x"), "Trop de tentatives échouées")

    def test_minutes_remaining(self):
        self.assertEqual(throttle.minutes_remaining("alice"), 0)
        self.fail(times=5)
        remaining = throttle.minutes_remaining("alice")
        self.assertTrue(1 <= remaining <= throttle.WINDOW.total_seconds() / 60)
        self.assertContains(self.attempt(password=PASSWORD), f"encore {remaining} minute")

    def test_old_records_are_purged_when_a_new_failure_is_recorded(self):
        FailedLogin.objects.create(identifier="ancien")
        FailedLogin.objects.update(created_at=timezone.now() - 3 * throttle.WINDOW)
        self.fail(times=1)
        self.assertFalse(FailedLogin.objects.filter(identifier="ancien").exists())
        self.assertEqual(FailedLogin.objects.filter(identifier="alice").count(), 1)

    def test_login_by_email_is_throttled_under_its_own_identifier(self):
        self.fail("alice@example.com", times=5)
        self.assertTrue(throttle.is_locked("alice@example.com"))
        self.assertFalse(throttle.is_locked("alice"))

    def test_admin_login_is_protected_too(self):
        User.objects.create_user("chef", "chef@example.com", PASSWORD, is_staff=True)
        admin_login = "/admin/login/?next=/admin/"
        for _ in range(5):
            self.client.post(admin_login, {"username": "chef", "password": "faux", "next": "/admin/"})
        blocked = self.client.post(admin_login, {"username": "chef", "password": PASSWORD, "next": "/admin/"})
        self.assertEqual(blocked.status_code, 200)  # reste sur le formulaire : pas de redirection
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_blank_identifier_is_never_recorded_or_locked(self):
        throttle.record_failure("")
        throttle.record_failure(None)
        self.assertFalse(FailedLogin.objects.exists())
        self.assertFalse(throttle.is_locked(""))

    def test_failed_login_log_is_read_only_in_the_admin(self):
        from .admin import FailedLoginAdmin

        model_admin = FailedLoginAdmin(FailedLogin, admin_site=None)
        self.assertFalse(model_admin.has_add_permission(None))
        self.assertFalse(model_admin.has_change_permission(None))
