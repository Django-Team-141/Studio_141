import re

from django.test import TestCase

from core.i18n import TEXTS
from core.models import TeamMember

EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")


class AboutPageTests(TestCase):
    def test_page_opens_in_both_languages(self):
        fa = self.client.get("/fa/about/")
        en = self.client.get("/en/about/")
        self.assertEqual(fa.status_code, 200)
        self.assertEqual(en.status_code, 200)
        self.assertContains(fa, "سایتتان را")
        self.assertContains(en, "tailored")

    def test_search_engine_tags_and_language_switch(self):
        r = self.client.get("/en/about/")
        self.assertContains(r, '<link rel="canonical" href="http://testserver/en/about/">')
        self.assertContains(r, 'hreflang="fa" href="http://testserver/fa/about/"')
        self.assertContains(r, 'href="/fa/about/"')

    def test_page_has_all_its_sections(self):
        body = self.client.get("/en/about/").content.decode()
        for section in ('id="why"', 'id="gets"', 'id="work"', 'id="process"'):
            self.assertIn(section, body)
        self.assertEqual(body.count('class="card get reveal"'), len(TEXTS["en"]["ap_gets"]))

    def test_call_to_action_links_to_the_form_and_contact(self):
        r = self.client.get("/en/about/")
        self.assertContains(r, 'href="/en/#order"')
        self.assertContains(r, 'href="/en/#contact"')

    def test_team_shows_only_when_there_are_members(self):
        self.assertNotContains(self.client.get("/en/about/"), 'id="team"')
        TeamMember.objects.create(name="Sara", role_fa="توسعه‌دهنده", role_en="Developer")
        r = self.client.get("/en/about/")
        self.assertContains(r, 'id="team"')
        self.assertContains(r, "Sara")

    def test_home_and_footer_link_to_the_about_page(self):
        r = self.client.get("/en/")
        self.assertContains(r, 'href="/en/about/"')
        self.assertContains(self.client.get("/fa/privacy/"), 'href="/fa/about/"')

    def test_sitemap_lists_the_about_page(self):
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("http://testserver/fa/about/", body)
        self.assertIn("http://testserver/en/about/", body)


class AboutTextsTests(TestCase):
    def test_benefit_lists_match_in_both_languages(self):
        fa, en = TEXTS["fa"]["ap_gets"], TEXTS["en"]["ap_gets"]
        self.assertEqual(len(fa), len(en))
        for item in fa + en:
            self.assertTrue(item["e"] and item["t"] and item["d"])

    def test_page_title_and_description_have_no_emoji(self):
        for lang, texts in TEXTS.items():
            for key in ("ap_title", "ap_meta"):
                self.assertIsNone(EMOJI.search(texts[key]), f"{lang}.{key} has an emoji")