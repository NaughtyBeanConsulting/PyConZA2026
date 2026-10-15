from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserManagerTests(TestCase):
    def test_email_is_the_username(self):
        user = User.objects.create_user("Ann@Example.COM", "s3cret-pass")
        self.assertEqual(User.USERNAME_FIELD, "email")
        self.assertFalse(hasattr(user, "username") and user.username)
        self.assertEqual(user.email, "ann@example.com")
        self.assertFalse(user.is_staff)

    def test_login_ignores_email_case(self):
        User.objects.create_user("ann@example.com", "s3cret-pass")
        self.assertIsNotNone(authenticate(username="ANN@example.com", password="s3cret-pass"))

    def test_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user("", "s3cret-pass")

    def test_create_superuser(self):
        admin = User.objects.create_superuser("boss@example.com", "s3cret-pass")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_display_name_never_shows_full_email(self):
        self.assertEqual(User(email="ann@example.com").display_name, "ann")
        self.assertEqual(User(email="ann@example.com", first_name="Ann", last_name="Lee").display_name, "Ann Lee")


class UserAdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("boss@example.com", "s3cret-pass")
        self.client.force_login(self.admin)

    def test_add_user_through_admin(self):
        response = self.client.post(
            reverse("admin:accounts_user_add"),
            {
                "email": "New@Example.com",
                "usable_password": "true",
                "password1": "a-Long-pass-123",
                "password2": "a-Long-pass-123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_admin_pages_render(self):
        for url in (
            reverse("admin:accounts_user_changelist"),
            reverse("admin:accounts_user_add"),
            reverse("admin:accounts_user_change", args=[self.admin.pk]),
            reverse("admin:auth_group_changelist"),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
