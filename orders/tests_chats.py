import urllib.error

from django.test import TestCase, override_settings

from orders import notify


class ChatIdTests(TestCase):
    @override_settings(
        TELEGRAM_CHAT_ID="111", TELEGRAM_CHAT_ID_2="222, 333",
        TELEGRAM_CHAT_ID_3="", TELEGRAM_CHAT_ID_4="111",
    )
    def test_all_slots_are_merged_without_repeats(self):
        self.assertEqual(notify.chat_ids(), ["111", "222", "333"])

    @override_settings(TELEGRAM_CHAT_ID="abc, 444")
    def test_values_that_are_not_numbers_are_ignored(self):
        self.assertEqual(notify.chat_ids(), ["444"])

    @override_settings(TELEGRAM_CHAT_ID="-1001234567890")
    def test_group_ids_with_a_minus_are_kept(self):
        self.assertEqual(notify.chat_ids(), ["-1001234567890"])

    @override_settings(TELEGRAM_CHAT_ID="", TELEGRAM_CHAT_ID_2="")
    def test_nothing_set_means_no_chats(self):
        self.assertEqual(notify.chat_ids(), [])

    def test_error_label_has_the_http_code_but_no_address(self):
        err = urllib.error.HTTPError(
            "https://api.telegram.org/botSECRET/sendMessage", 403, "Forbidden", {}, None
        )
        label = notify.error_label(err)
        self.assertEqual(label, "HTTPError 403")
        self.assertNotIn("SECRET", label)