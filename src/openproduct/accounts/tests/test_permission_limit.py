from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa

from .factories import UserFactory


@disable_admin_mfa()
class SmokeTests(WebTest):
    """
    Test that the django user pages still load with whatever modifications we made.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.superuser = UserFactory.create(superuser=True)

    def test_user_list(self):
        url = reverse("admin:accounts_user_changelist")

        response = self.app.get(url, user=self.superuser)

        self.assertEqual(response.status_code, 200)

    def test_user_change(self):
        user = UserFactory.create()
        url = reverse("admin:accounts_user_change", args=(user.pk,))

        response = self.app.get(url, user=self.superuser)

        self.assertEqual(response.status_code, 200)

    def test_user_add(self):
        url = reverse("admin:accounts_user_add")

        response = self.app.get(url, user=self.superuser)

        self.assertEqual(response.status_code, 200)


@disable_admin_mfa()
class PasswordResetViewTests(TestCase):
    def setUp(self):
        super().setUp()

        self.superuser = UserFactory.create(
            username="superuser",
            password="secret",
            superuser=True,
        )
        self.other_superuser = UserFactory.create(
            username="other_superuser",
            password="secret",
            superuser=True,
        )

        self.less_perms_staff_user = UserFactory.create(
            username="less_perms_staff_user",
            password="secret",
            is_staff=True,
        )
        for p in Permission.objects.filter(
            content_type=ContentType.objects.get(app_label="accounts", model="user")
        ):
            self.less_perms_staff_user.user_permissions.add(p)

        self.more_perms_staff_user = UserFactory.create(
            username="more_perms_staff_user",
            password="secret",
            is_staff=True,
        )
        for p in Permission.objects.all():
            self.more_perms_staff_user.user_permissions.add(p)

    def _change_user(self, target_user, as_user):
        self.client.force_login(as_user)

        response = self.client.post(
            reverse("admin:accounts_user_change", args=(target_user.pk,)),
            {
                "username": "example",
                "date_joined_0": "2022-01-01",
                "date_joined_1": "12:00:00",
                "_save": "1",
            },
        )
        return response

    def test_change_user_as_superuser(self):
        response = self._change_user(
            target_user=self.other_superuser, as_user=self.superuser
        )
        self.assertEqual(response.status_code, 302, response.content)

    def test_change_superuser_as_non_superuser(self):
        response = self._change_user(
            target_user=self.superuser, as_user=self.more_perms_staff_user
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_change_user_as_user_with_less_permissions(self):
        response = self._change_user(
            target_user=self.more_perms_staff_user, as_user=self.less_perms_staff_user
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_change_user_as_user_with_more_permissions(self):
        response = self._change_user(
            target_user=self.less_perms_staff_user, as_user=self.more_perms_staff_user
        )
        self.assertEqual(response.status_code, 302, response.content)

    def _change_password_page(self, target_user, as_user):
        self.client.force_login(as_user)

        change_password_url = "{}{}/password/".format(
            reverse("admin:accounts_user_changelist"), target_user.pk
        )
        response = self.client.get(change_password_url, follow=True)
        return response

    def test_change_password_as_superuser(self):
        response = self._change_password_page(
            target_user=self.other_superuser, as_user=self.superuser
        )
        self.assertEqual(response.status_code, 200, response.content)

    def test_change_password_as_non_superuser(self):
        response = self._change_password_page(
            target_user=self.superuser, as_user=self.more_perms_staff_user
        )
        self.assertEqual(response.status_code, 403, response.content)

    def test_change_password_as_user_with_less_permissions(self):
        response = self._change_password_page(
            target_user=self.more_perms_staff_user, as_user=self.less_perms_staff_user
        )
        self.assertEqual(response.status_code, 403, response.content)

    def test_change_password_as_user_with_more_permissions(self):
        response = self._change_password_page(
            target_user=self.less_perms_staff_user, as_user=self.more_perms_staff_user
        )
        self.assertEqual(response.status_code, 200, response.content)
