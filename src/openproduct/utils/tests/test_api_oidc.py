from functools import partial

from django.urls import reverse
from django.utils.translation import gettext as _

from django_webtest import WebTest
from maykin_common.vcr import VCRMixin

from openproduct.accounts.models import User
from openproduct.accounts.tests.factories import UserFactory
from openproduct.utils.tests.keycloak import keycloak_login, mock_oidc_db_config

mock_admin_oidc_config = partial(
    mock_oidc_db_config,
    app_label="mozilla_django_oidc_db",
    model="OpenIDConnectConfig",
    id=1,  # required for the group queries because we're using in-memory objects
    make_users_staff=True,
    username_claim=["preferred_username"],
)


class OIDCFLowTests(VCRMixin, WebTest):
    @mock_admin_oidc_config()
    def test_duplicate_email_unique_constraint_violated(self):
        # this user collides on the email address
        staff_user = UserFactory.create(
            username="no-match",
            email="admin@example.com",
            is_staff=True,
        )
        login_page = self.app.get(reverse("admin:login"))
        start_response = login_page.click(
            description=_("Login with organization account")
        )
        assert start_response.status_code == 302
        redirect_uri = keycloak_login(
            start_response["Location"], username="admin", password="admin"
        )

        error_page = self.app.get(redirect_uri, auto_follow=True)

        with self.subTest("error page"):
            self.assertEqual(error_page.status_code, 200)
            self.assertEqual(error_page.request.path, reverse("admin-oidc-error"))
            self.assertEqual(
                error_page.context["oidc_error"],
                'duplicate key value violates unique constraint "filled_email_unique"\n'
                "DETAIL:  Key (email)=(admin@example.com) already exists.",
            )
            self.assertContains(
                error_page, "duplicate key value violates unique constraint"
            )

        with self.subTest("user state unmodified"):
            self.assertEqual(User.objects.count(), 1)
            staff_user.refresh_from_db()
            self.assertEqual(staff_user.username, "no-match")
            self.assertEqual(staff_user.email, "admin@example.com")
            self.assertTrue(staff_user.is_staff)

    @mock_admin_oidc_config()
    def test_happy_flow(self):
        login_page = self.app.get(reverse("admin:login"))
        start_response = login_page.click(
            description=_("Login with organization account")
        )
        assert start_response.status_code == 302
        redirect_uri = keycloak_login(
            start_response["Location"], username="admin", password="admin"
        )

        admin_index = self.app.get(redirect_uri, auto_follow=True)

        self.assertEqual(admin_index.status_code, 200)
        self.assertEqual(admin_index.request.path, reverse("admin:index"))

        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.username, "admin")

    @mock_admin_oidc_config(make_users_staff=False)
    def test_happy_flow_existing_user(self):
        staff_user = UserFactory.create(
            username="admin",
            email="update-me",
            is_staff=True,
        )
        login_page = self.app.get(reverse("admin:login"))
        start_response = login_page.click(
            description=_("Login with organization account")
        )
        assert start_response.status_code == 302
        redirect_uri = keycloak_login(
            start_response["Location"], username="admin", password="admin"
        )

        admin_index = self.app.get(redirect_uri, auto_follow=True)

        self.assertEqual(admin_index.status_code, 200)
        self.assertEqual(admin_index.request.path, reverse("admin:index"))

        self.assertEqual(User.objects.count(), 1)
        staff_user.refresh_from_db()
        self.assertEqual(staff_user.username, "admin")
        self.assertEqual(staff_user.email, "admin@example.com")
