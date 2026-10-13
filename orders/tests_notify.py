import io
from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings

from orders import notify
from orders.models import Order
from plans.models import Plan


class ImmediateThread:
    """جای Thread واقعی؛ کار را همان لحظه انجام می‌دهد تا تست‌ها منتظر نمانند."""

    def __init__(self, target=None, args=(), daemon=None, **kwargs):
        self.target = target
        self.args = args

    def start(self):
        self.target(*self.args)


def make_order(**extra):
    data = dict(
        name="Sara Karimi", phone="09121234567", email="sara@example.com",
        message="I need a shop", code="141-ABC234", lang="fa",
    )
    data.update(extra)
    return Order(**data)


def make_plan():
    return Plan.objects.create(
        kind="shop", level=2, title_fa="هوشمند", title_en="Smart",
        price_fa="از X تومان", price_en="from X",
    )


@override_settings(TELEGRAM_FULL_DETAILS=True)
class FullMessageTests(TestCase):
    def test_message_follows_the_form_and_has_the_code(self):
        text = notify.build_text(make_order(plan=make_plan()))
        for part in (
            "141-ABC234", "Sara Karimi", "09121234567", "sara@example.com",
            "I need a shop", "فروشگاهی", "هوشمند", "از X تومان",
        ):
            self.assertIn(part, text)

    def test_customer_text_cannot_break_the_html(self):
        text = notify.build_text(make_order(name="<b>x</b>", message="a & b <script>"))
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", text)
        self.assertIn("a &amp; b &lt;script&gt;", text)
        self.assertNotIn("<script>", text)

    def test_empty_optional_fields_show_a_dash(self):
        text = notify.build_text(make_order(email="", message=""))
        self.assertIn("انتخاب نشده", text)
        self.assertIn("—", text)


class TelegramChannelTests(TestCase):
    @override_settings(TELEGRAM_BOT_TOKEN="t", TELEGRAM_CHAT_ID="111, 222")
    def test_message_goes_to_every_chat_as_html(self):
        with patch("orders.notify.threading.Thread", ImmediateThread), \
                patch("orders.notify.api") as api:
            notify.notify_new_order(make_order())

        self.assertEqual(api.call_count, 2)
        sent = [call.args[1] for call in api.call_args_list]
        self.assertEqual([s["chat_id"] for s in sent], ["111", "222"])
        self.assertTrue(all(s["parse_mode"] == "HTML" for s in sent))

    @override_settings(TELEGRAM_BOT_TOKEN="t", TELEGRAM_CHAT_ID="111,222")
    def test_one_failing_chat_does_not_stop_the_others(self):
        reached = []

        def fake_api(method, payload=None, timeout=8):
            reached.append(payload["chat_id"])
            if payload["chat_id"] == "111":
                raise OSError("blocked")

        with patch("orders.notify.threading.Thread", ImmediateThread), \
                patch("orders.notify.api", side_effect=fake_api):
            notify.notify_new_order(make_order())

        self.assertEqual(reached, ["111", "222"])


class EmailChannelTests(TestCase):
    @override_settings(
        EMAIL_HOST="smtp.example.com", ORDER_NOTIFY_EMAIL_TO=["team@example.com"],
        TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="",
    )
    def test_email_has_the_form_and_replies_go_to_the_customer(self):
        with patch("orders.notify.threading.Thread", ImmediateThread):
            notify.notify_new_order(make_order())

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["team@example.com"])
        self.assertIn("141-ABC234", message.subject)
        for part in ("Sara Karimi", "09121234567", "sara@example.com", "I need a shop"):
            self.assertIn(part, message.body)
        self.assertEqual(message.reply_to, ["sara@example.com"])

    @override_settings(EMAIL_HOST="smtp.example.com", ORDER_NOTIFY_EMAIL_TO=["team@example.com"])
    def test_no_reply_address_when_the_customer_gave_no_email(self):
        with patch("orders.notify.threading.Thread", ImmediateThread):
            notify.notify_new_order(make_order(email=""))
        self.assertEqual(mail.outbox[0].reply_to, [])

    @override_settings(EMAIL_HOST="", ORDER_NOTIFY_EMAIL_TO=["team@example.com"])
    def test_email_needs_a_mail_server(self):
        with patch("orders.notify.threading.Thread", ImmediateThread):
            notify.notify_new_order(make_order())
        self.assertEqual(mail.outbox, [])

    @override_settings(EMAIL_HOST="smtp.example.com", ORDER_NOTIFY_EMAIL_TO=[])
    def test_email_needs_a_recipient(self):
        with patch("orders.notify.threading.Thread", ImmediateThread):
            notify.notify_new_order(make_order())
        self.assertEqual(mail.outbox, [])


class EndToEndTests(TestCase):
    def setUp(self):
        cache.clear()

    @override_settings(TELEGRAM_BOT_TOKEN="t", TELEGRAM_CHAT_ID="111", TELEGRAM_FULL_DETAILS=True)
    def test_a_submitted_request_reaches_telegram_with_its_code(self):
        with patch("orders.notify.threading.Thread", ImmediateThread), \
                patch("orders.notify.api") as api, \
                self.captureOnCommitCallbacks(execute=True):
            self.client.post("/fa/order/", {
                "name": "Sara", "phone": "09121234567", "email": "",
                "plan": "", "message": "A small site", "website": "",
            })

        order = Order.objects.get()
        text = api.call_args.args[1]["text"]
        self.assertIn(order.code, text)
        self.assertIn("Sara", text)
        self.assertIn("09121234567", text)


class NotifyTestCommandTests(TestCase):
    @override_settings(
        TELEGRAM_BOT_TOKEN="t", TELEGRAM_CHAT_ID="111",
        EMAIL_HOST="smtp.example.com", ORDER_NOTIFY_EMAIL_TO=["team@example.com"],
    )
    def test_sample_goes_through_every_channel(self):
        out = io.StringIO()
        with patch("orders.notify.api") as api:
            call_command("notify_test", stdout=out)

        api.assert_called_once()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("141-TEST22", mail.outbox[0].subject)
        self.assertIn("Telegram: sent to chat 1 (111)", out.getvalue())