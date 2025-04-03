.. _client-development-auth:

Authentication and authorization
================================

Open Product uses the described authentication and authorization mechanism based on
API tokens. It does not implement its own mechanism but uses `TokenAuthentication`_
provided by `Django REST Framework`_ and `OIDCAuthentication` provided by `mozilla-django-oidc`_ in combination with `mozilla-django-oidc-db`_.


Token
-----

To connect to Open Product, you have received a token key which should be included
in your request's HTTP headers:

.. code-block:: none

   Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b


OpenID connect
--------------

To connect to Open Product, you have received a jwt token which should be included
in your request's HTTP headers:

.. code-block:: none

   Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cC.....


.. _TokenAuthentication: https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
.. _Django REST Framework: https://www.django-rest-framework.org/
.. _mozilla-django-oidc: https://mozilla-django-oidc.readthedocs.io/en/stable/drf.html
.. _mozilla-django-oidc-db: https://mozilla-django-oidc-db.readthedocs.io/en/latest/
