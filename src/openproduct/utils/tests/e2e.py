import os
from typing import Any, Literal  # noqa

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, tag
from django.urls import reverse

from maykin_2fa.test import disable_admin_mfa
from playwright.sync_api import (
    Browser,
    BrowserType,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

type SupportedBrowser = Literal["chromium", "firefox", "webkit"]

HEADLESS = "NO_E2E_HEADLESS" not in os.environ
BROWSER: SupportedBrowser = os.getenv("E2E_DRIVER", default="chromium")
BROWSER_PERMISSIONS: dict[SupportedBrowser, list[str]] = {
    "chromium": ["clipboard-read", "clipboard-write"],
}

BROWSER_ARGS: dict[SupportedBrowser, list[str]] = {
    "chromium": ["--no-sandbox", "--disable-dev-shm-usage"],
}

DEFAULT_PASSWORD = "secret"


@tag("e2e")
@disable_admin_mfa()
@override_settings(ALLOWED_HOSTS=["*"])
class E2ETestCase(StaticLiveServerTestCase):
    playwright: Playwright
    browser: Browser

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()

        cls.playwright = sync_playwright().start()
        cls.addClassCleanup(cls.playwright.stop)

        browser_type: BrowserType = getattr(cls.playwright, BROWSER)
        cls.browser = browser_type.launch(
            headless=HEADLESS,
            args=BROWSER_ARGS.get(BROWSER, []),
        )
        cls.addClassCleanup(cls.browser.close)

    @classmethod
    def live_reverse(cls, viewname, args=None, kwargs=None) -> str:
        path = reverse(viewname, args=args, kwargs=kwargs)
        return f"{cls.live_server_url}{path}"

    def _context_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "locale": "en-UK",
            "timezone_id": "Europe/Amsterdam",
        }
        if permissions := BROWSER_PERMISSIONS.get(BROWSER):
            kwargs["permissions"] = permissions
        return kwargs

    def get_user_login_state(self, user, password=DEFAULT_PASSWORD) -> dict:
        context = self.browser.new_context(**self._context_kwargs())
        try:
            page = context.new_page()
            page.goto(self.live_reverse("admin:login"))

            page.locator("#id_auth-username").fill(user.username)
            page.locator("#id_auth-password").fill(password)
            page.get_by_role("button", name="Aanmelden").click()
            try:
                page.wait_for_selector("#site-name", timeout=5000)
            except PlaywrightTimeoutError:
                self.fail(f"Login failed for {user.username}. Current URL: {page.url}")

            return context.storage_state()
        finally:
            context.close()

    def new_page(self, user=None, password=DEFAULT_PASSWORD) -> Page:
        state = self.get_user_login_state(user, password) if user else None
        context = self.browser.new_context(
            storage_state=state, **self._context_kwargs()
        )
        self.addCleanup(context.close)
        return context.new_page()
