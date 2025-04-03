from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from openproduct.accounts.models import User


class BaseApiTestCase(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
