import io
import re

from django.core.management import call_command
from django.test import TestCase

from core.i18n import TEXTS
from core.management.commands.refresh_content import OLD_FAQ, OLD_PROJECT_DESC_EN
from core.management.commands.seed_faq import DATA as FAQ_DATA
from core.models import FaqItem
from portfolio.management.commands.seed_portfolio import STARTERS
from portfolio.models import Project

# ایموجی‌ها (به‌علاوه‌ی علامت تغییر شکلشان)
EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")


class TextsTests(TestCase):
    def test_both_languages_have_the_same_keys(self):
        self.assertEqual(set(TEXTS["fa"]), set(TEXTS["en"]))

    def test_no_text_is_empty(self):
        for lang, texts in TEXTS.items():
            for key, value in texts.items():
                self.assertTrue(value, f"{lang}.{key} is empty")

    def test_process_steps_match_in_both_languages(self):
        fa, en = TEXTS["fa"]["process_steps"], TEXTS["en"]["process_steps"]
        self.assertEqual(len(fa), len(en))
        for step in fa + en:
            self.assertTrue(step["t"] and step["d"])

    def test_search_results_and_privacy_text_have_no_emoji(self):
        plain = ["title_home", "meta_desc"] + [k for k in TEXTS["fa"] if k.startswith("pv_")]
        for lang, texts in TEXTS.items():
            for key in plain:
                self.assertIsNone(EMOJI.search(texts[key]), f"{lang}.{key} has an emoji")


class DecorationTests(TestCase):
    def test_home_sections_have_emoji_chips(self):
        body = self.client.get("/en/").content.decode()
        self.assertGreaterEqual(body.count('class="emo"'), 6)


class NotFoundPageTests(TestCase):
    def test_unknown_address_shows_the_friendly_404(self):
        r = self.client.get("/en/this-page-does-not-exist/")
        self.assertContains(r, "find that page", status_code=404)
        self.assertContains(r, 'href="/en/"', status_code=404)


class RefreshContentTests(TestCase):
    def _run(self):
        out = io.StringIO()
        call_command("refresh_content", stdout=out)
        return out.getvalue()

    def test_old_faq_is_replaced_and_edited_faq_is_left_alone(self):
        old_q, old_a = OLD_FAQ[0]
        FaqItem.objects.create(
            question_fa="سؤال قدیمی", question_en=old_q,
            answer_fa="جواب قدیمی", answer_en=old_a, order=0,
        )
        edited_q, _ = OLD_FAQ[1]
        FaqItem.objects.create(
            question_fa="سؤال ویرایش‌شده", question_en=edited_q,
            answer_fa="جواب ما", answer_en="Our own answer", order=1,
        )

        self._run()

        first = FaqItem.objects.get(question_en=FAQ_DATA[0][1])
        self.assertEqual(first.answer_en, FAQ_DATA[0][3])
        self.assertEqual(first.answer_fa, FAQ_DATA[0][2])
        self.assertTrue(
            FaqItem.objects.filter(question_en=edited_q, answer_en="Our own answer").exists()
        )
        # یکی به‌روز شد، یکی ویرایش‌شده ماند، و سه تای باقی‌مانده اضافه شدند
        self.assertEqual(FaqItem.objects.count(), 5)

    def test_running_twice_changes_nothing_more(self):
        self._run()
        self._run()
        self.assertEqual(FaqItem.objects.count(), 5)

    def test_old_project_text_is_refreshed(self):
        Project.objects.create(
            title="CarZone", slug="carzone",
            desc_fa="قدیمی", desc_en=OLD_PROJECT_DESC_EN["carzone"],
        )
        self._run()
        new = next(s for s in STARTERS if s["slug"] == "carzone")
        project = Project.objects.get(slug="carzone")
        self.assertEqual(project.desc_en, new["desc_en"])
        self.assertEqual(project.desc_fa, new["desc_fa"])

    def test_edited_project_text_is_not_touched(self):
        Project.objects.create(
            title="CarZone", slug="carzone",
            desc_fa="نوشته‌ی خودمان", desc_en="Written by the team",
        )
        self._run()
        self.assertEqual(Project.objects.get(slug="carzone").desc_en, "Written by the team")