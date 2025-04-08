from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from maykin_2fa import monkeypatch_admin
from maykin_2fa.urls import urlpatterns, webauthn_urlpatterns
from mozilla_django_oidc_db.views import AdminLoginFailure

from openproduct.accounts.views.password_reset import PasswordResetView
from openproduct.producten.urls import urlpatterns as product_urlpatterns
from openproduct.producttypen.urls import urlpatterns as producttype_urlpatterns

# Configure admin

monkeypatch_admin()

handler500 = "openproduct.utils.views.server_error"

admin.site.enable_nav_sidebar = False
admin.site.site_header = "Open Product admin"
admin.site.site_title = "Open Product admin"
admin.site.index_title = "Open Product dashboard"

# URL routing

urlpatterns = [
    path(
        "admin/password_reset/",
        PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    # OIDC urls
    path("admin/login/failure/", AdminLoginFailure.as_view(), name="admin-oidc-error"),
    path("auth/oidc/", include("mozilla_django_oidc.urls")),
    # Use custom login views for the admin + support hardware tokens
    path("admin/", include((urlpatterns, "maykin_2fa"))),
    path("admin/", include((webauthn_urlpatterns, "two_factor"))),
    path("admin/", admin.site.urls),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "",
        TemplateView.as_view(
            template_name="index.html",
        ),
        name="home",
    ),
    path(
        "producttypen/api/v{}/".format(settings.PRODUCTTYPEN_API_MAJOR_VERSION),
        include(producttype_urlpatterns),
    ),
    path(
        "producten/api/v{}/".format(settings.PRODUCTEN_API_MAJOR_VERSION),
        include(product_urlpatterns),
    ),
    path("ref/", include("notifications_api_common.urls")),
    # path("view-config/", ViewConfigView.as_view(), name="view-config"),
]

# NOTE: The staticfiles_urlpatterns also discovers static files (ie. no need to run collectstatic). Both the static
# folder and the media folder are only served via Django if DEBUG = True.
urlpatterns += staticfiles_urlpatterns() + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG and apps.is_installed("debug_toolbar"):
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        path("favicon.ico", RedirectView.as_view(url="/static/ico/favicon.png")),
    ] + urlpatterns
