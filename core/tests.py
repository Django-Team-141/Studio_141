import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory, TestCase, override_settings
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_static.models import StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from core import lockout
from core.models import FaqItem, SiteSettings, TeamMember
from core.utils import client_ip

User = get_user_model()
PASSWORD = "a-long-test-password-1"


class LanguageAndSeoTests(TestCase):
    def test_root_redirects_by_browser_language(self):
        r = self.client.get("/")
        self.assertRedirects(r, "/fa/", fetch_redirect_response=False)
        r = self.client.get("/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertRedirects(r, "/en/", fetch_redirect_response=False)

    def test_each_language_has_its_own_page(self):
        fa = self.client.get("/fa/")
        en = self.client.get("/en/")
        self.assertEqual(fa.status_code, 200)
        self.assertContains(fa, 'lang="fa" dir="rtl"')
        self.assertContains(fa, "هر پروژه")
        self.assertContains(en, 'lang="en" dir="ltr"')
        self.assertContains(en, "Every project,")

    def test_language_switch_keeps_the_same_page(self):
        r = self.client.get("/fa/privacy/")
        self.assertContains(r, 'href="/en/privacy/"')
        r = self.client.get("/en/privacy/")
        self.assertContains(r, 'href="/fa/privacy/"')

    def test_search_engine_tags(self):
        r = self.client.get("/en/")
        self.assertContains(r, '<link rel="canonical" href="http://testserver/en/">')
        self.assertContains(r, 'hreflang="fa" href="http://testserver/fa/"')
        self.assertContains(r, 'hreflang="x-default" href="http://testserver/"')
        self.assertContains(r, "application/ld+json")

    def test_privacy_pages_open(self):
        self.assertEqual(self.client.get("/fa/privacy/").status_code, 200)
        self.assertEqual(self.client.get("/en/privacy/").status_code, 200)

    def test_old_address_without_language_redirects(self):
        r = self.client.get("/privacy/")
        self.assertRedirects(r, "/fa/privacy/", fetch_redirect_response=False)

    def test_sitemap_lists_both_languages(self):
        r = self.client.get("/sitemap.xml")
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        for url in (
            "http://testserver/fa/",
            "http://testserver/en/",
            "http://testserver/fa/privacy/",
            "http://testserver/en/privacy/",
        ):
            self.assertIn(url, body)
        self.assertIn("xhtml:link", body)

    def test_robots_txt(self):
        body = self.client.get("/robots.txt").content.decode()
        self.assertIn("Disallow: /fa/order/", body)
        self.assertIn("Disallow: /en/order/", body)
        self.assertIn("Sitemap: http://testserver/sitemap.xml", body)
        # آدرس مخفی ادمین نباید لو برود
        self.assertNotIn(settings.ADMIN_URL, body)

    def test_security_headers_on_public_pages(self):
        r = self.client.get("/fa/")
        csp = r["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertNotIn("google", csp)
        self.assertEqual(r["X-Frame-Options"], "DENY")
        self.assertEqual(r["X-Content-Type-Options"], "nosniff")

    def test_admin_is_not_indexed(self):
        r = self.client.get("/" + settings.ADMIN_URL)
        self.assertEqual(r["X-Robots-Tag"], "noindex, nofollow")
        self.assertNotIn("Content-Security-Policy", r)


class SiteSettingsTests(TestCase):
    def test_texts_can_be_overridden_per_language(self):
        SiteSettings.objects.create(hero_a_en="Hello there")
        self.assertContains(self.client.get("/en/"), "Hello there")
        fa = self.client.get("/fa/")
        self.assertNotContains(fa, "Hello there")
        self.assertContains(fa, "هر پروژه")

    @override_settings(CONTACT_TELEGRAM="env_studio")
    def test_env_contact_is_used_when_admin_is_empty(self):
        self.assertContains(self.client.get("/fa/"), "https://t.me/env_studio")

    @override_settings(CONTACT_TELEGRAM="env_studio")
    def test_admin_value_wins_over_env(self):
        SiteSettings.objects.create(telegram="@admin_studio")
        r = self.client.get("/fa/")
        self.assertContains(r, "https://t.me/admin_studio")
        self.assertNotContains(r, "env_studio")

    @override_settings(CONTACT_TELEGRAM="bad name!")
    def test_bad_username_is_ignored(self):
        self.assertNotContains(self.client.get("/fa/"), "t.me/")

    def test_footer_shows_the_email(self):
        SiteSettings.objects.create(email="hi@example.com")
        self.assertContains(self.client.get("/en/"), "mailto:hi@example.com")

    def test_faq_and_team_show_only_published(self):
        FaqItem.objects.create(
            question_fa="س۱", question_en="Shown question",
            answer_fa="ج", answer_en="a1", is_published=True,
        )
        FaqItem.objects.create(
            question_fa="س۲", question_en="Hidden question",
            answer_fa="ج", answer_en="a2", is_published=False,
        )
        TeamMember.objects.create(name="Sara", role_fa="توسعه‌دهنده", role_en="Developer")
        r = self.client.get("/en/")
        self.assertContains(r, "Shown question")
        self.assertNotContains(r, "Hidden question")
        self.assertContains(r, "Sara")
        self.assertContains(r, "Developer")

    def test_seed_faq_can_run_twice(self):
        call_command("seed_faq", stdout=io.StringIO())
        call_command("seed_faq", stdout=io.StringIO())
        self.assertEqual(FaqItem.objects.count(), 5)


class LockoutTests(TestCase):
    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()
        self.user = User.objects.create_user("alice", password=PASSWORD)

    def _req(self, ip="10.0.0.1"):
        return self.factory.post("/", REMOTE_ADDR=ip)

    def test_right_password_works_before_any_lockout(self):
        user = authenticate(self._req(), username="alice", password=PASSWORD)
        self.assertEqual(user, self.user)

    def test_five_wrong_passwords_lock_the_account(self):
        req = self._req()
        for _ in range(5):
            self.assertIsNone(authenticate(req, username="alice", password="wrong"))
        self.assertTrue(lockout.is_locked(req, "alice"))
        # حتی رمز درست هم تا پایان قفل قبول نمی‌شود
        self.assertIsNone(authenticate(req, username="alice", password=PASSWORD))

    def test_lock_does_not_touch_other_visitors(self):
        for _ in range(5):
            lockout.record_failure(self._req("10.0.0.1"), "alice")
        self.assertTrue(lockout.is_locked(self._req("10.0.0.1"), "alice"))
        self.assertFalse(lockout.is_locked(self._req("10.0.0.2"), "bob"))

    def test_the_lock_also_covers_the_same_address(self):
        for _ in range(5):
            lockout.record_failure(self._req("10.0.0.1"), "alice")
        # همان IP با نام کاربری دیگر هم قفل است (عمدی)
        self.assertTrue(lockout.is_locked(self._req("10.0.0.1"), "bob"))


class ClientIpTests(TestCase):
    def test_proxy_header_is_ignored_by_default(self):
        req = RequestFactory().get("/", REMOTE_ADDR="9.9.9.9", HTTP_X_REAL_IP="1.2.3.4")
        self.assertEqual(client_ip(req), "9.9.9.9")

    @override_settings(TRUST_PROXY=True)
    def test_proxy_header_is_used_behind_our_own_proxy(self):
        req = RequestFactory().get("/", REMOTE_ADDR="9.9.9.9", HTTP_X_REAL_IP="1.2.3.4")
        self.assertEqual(client_ip(req), "1.2.3.4")


class AdminTwoFactorTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = User.objects.create_superuser("boss", password=PASSWORD)
        self.url = "/" + settings.ADMIN_URL

    def test_password_alone_is_not_enough(self):
        self.client.force_login(self.admin)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 302)
        self.assertIn("login", r["Location"])

    def test_verified_staff_gets_in(self):
        device = TOTPDevice.objects.create(user=self.admin, name="test", confirmed=True)
        self.client.force_login(self.admin)
        session = self.client.session
        session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        session.save()
        self.assertEqual(self.client.get(self.url).status_code, 200)


class Setup2faCommandTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user("alice", password=PASSWORD, is_staff=True)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def _run(self, *args):
        out = io.StringIO()
        # فایل‌ها داخل پوشه‌ی موقت می‌روند، نه پوشه‌ی پروژه.
        # QR در حالت ترمینال روی sys.stdout چاپ می‌شود؛ اینجا خروجی‌اش را می‌گیریم.
        with self.settings(TWO_FA_OUTPUT_DIR=self.dir), redirect_stdout(io.StringIO()):
            call_command("setup_2fa", *args, "--no-open", stdout=out)
        return out.getvalue()

    def _tokens(self):
        return list(
            StaticToken.objects.filter(device__user=self.staff).values_list("token", flat=True)
        )

    def test_default_mode_saves_a_qr_image_and_a_recovery_file(self):
        out = self._run("alice")

        self.assertEqual(TOTPDevice.objects.filter(user=self.staff, confirmed=True).count(), 1)
        tokens = self._tokens()
        self.assertEqual(len(tokens), 8)

        png = self.dir / "alice-qr.png"
        txt = self.dir / "alice-recovery-codes.txt"
        self.assertEqual(png.read_bytes()[:4], b"\x89PNG")
        text = txt.read_text(encoding="utf-8-sig")
        for token in tokens:
            self.assertIn(token, text)
            # در ترمینال هیچ کدی چاپ نمی‌شود
            self.assertNotIn(token, out)

    def test_terminal_mode_prints_the_codes_and_saves_no_files(self):
        out = self._run("alice", "--terminal")
        tokens = self._tokens()
        self.assertEqual(len(tokens), 8)
        for token in tokens:
            self.assertIn(token, out)
        self.assertEqual(list(self.dir.iterdir()), [])

    def test_second_run_needs_reset(self):
        self._run("alice")
        with self.assertRaises(CommandError):
            self._run("alice")
        self._run("alice", "--reset")
        self.assertEqual(TOTPDevice.objects.filter(user=self.staff).count(), 1)
        self.assertEqual(len(self._tokens()), 8)

    def test_non_staff_user_is_refused(self):
        User.objects.create_user("bob", password=PASSWORD)
        with self.assertRaises(CommandError):
            self._run("bob")

    def test_if_files_cannot_be_written_nothing_changes(self):
        with patch("core.management.commands.setup_2fa.segno.make", side_effect=OSError("disk full")):
            with self.assertRaises(CommandError):
                self._run("alice")
        self.assertEqual(TOTPDevice.objects.filter(user=self.staff).count(), 0)
        self.assertEqual(self._tokens(), [])