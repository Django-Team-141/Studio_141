from django.test import TestCase, override_settings

from core.models import SiteSettings


class ContactSectionTests(TestCase):
    def test_whatsapp_and_instagram_say_coming_soon_by_default(self):
        r = self.client.get("/en/")
        self.assertContains(r, 'id="contact"')
        self.assertContains(r, "data-soon=")
        self.assertContains(r, "WhatsApp isn")
        self.assertContains(r, "Our Instagram page isn")
        self.assertNotContains(r, "wa.me/")
        self.assertNotContains(r, "instagram.com/")
        self.assertContains(r, "js/contact.js")

    def test_whatsapp_becomes_a_real_link_when_switched_on(self):
        SiteSettings.objects.create(whatsapp="989121234567", whatsapp_live=True)
        r = self.client.get("/en/")
        self.assertContains(r, "https://wa.me/989121234567")
        self.assertNotContains(r, "WhatsApp isn")
        # اینستاگرام هنوز «به‌زودی» است
        self.assertContains(r, "Our Instagram page isn")

    def test_switch_without_a_valid_number_stays_coming_soon(self):
        SiteSettings.objects.create(whatsapp="abc", whatsapp_live=True)
        r = self.client.get("/en/")
        self.assertNotContains(r, "wa.me/")
        self.assertContains(r, "WhatsApp isn")

    def test_instagram_becomes_a_real_link_when_switched_on(self):
        SiteSettings.objects.create(instagram="studio_one", instagram_live=True)
        r = self.client.get("/en/")
        self.assertContains(r, "https://instagram.com/studio_one")
        self.assertNotContains(r, "Our Instagram page isn")

    def test_email_card_shows_the_address_and_links_to_it(self):
        SiteSettings.objects.create(email="team@example.com")
        r = self.client.get("/en/")
        self.assertContains(r, 'href="mailto:team@example.com"')
        self.assertContains(r, ">team@example.com<")

    @override_settings(CONTACT_EMAIL="env@example.com")
    def test_email_from_env_is_the_fallback(self):
        self.assertContains(self.client.get("/fa/"), 'href="mailto:env@example.com"')

    @override_settings(CONTACT_EMAIL="env@example.com")
    def test_email_from_admin_wins_over_env(self):
        SiteSettings.objects.create(email="admin@example.com")
        r = self.client.get("/fa/")
        self.assertContains(r, 'href="mailto:admin@example.com"')
        self.assertNotContains(r, "env@example.com")

    @override_settings(CONTACT_EMAIL="not an email")
    def test_bad_email_is_ignored(self):
        self.assertNotContains(self.client.get("/fa/"), "mailto:")

    @override_settings(CONTACT_TELEGRAM="studio_one")
    def test_telegram_card_shows_the_handle_and_links_to_it(self):
        r = self.client.get("/en/")
        self.assertContains(r, 'href="https://t.me/studio_one"')
        self.assertContains(r, ">@studio_one<")

    def test_search_engines_only_get_real_profiles(self):
        SiteSettings.objects.create(instagram="studio_one", instagram_live=False)
        r = self.client.get("/en/")
        self.assertContains(r, "application/ld+json")
        self.assertNotContains(r, "instagram.com/studio_one")