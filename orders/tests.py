import io
from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from orders import notify
from orders.models import Order
from plans.models import Plan

GOOD = {
    "name": "Sara",
    "phone": "09121234567",
    "email": "",
    "plan": "",
    "message": "A small site",
    "website": "",
}


class OrderFormTests(TestCase):
    def setUp(self):
        cache.clear()

    def _post(self, path="/fa/order/", **extra):
        return self.client.post(path, dict(GOOD, **extra))

    def test_good_request_is_saved_and_gets_a_code(self):
        r = self._post()
        self.assertRedirects(r, "/fa/order/done/", fetch_redirect_response=False)
        order = Order.objects.get()
        self.assertRegex(order.code, r"^141-[A-HJ-NP-Z2-9]{6}$")
        self.assertEqual(order.lang, "fa")
        self.assertEqual(self.client.session["last_order"], order.code)

    def test_english_request_remembers_the_language(self):
        r = self._post("/en/order/")
        self.assertRedirects(r, "/en/order/done/", fetch_redirect_response=False)
        self.assertEqual(Order.objects.get().lang, "en")

    def test_persian_digits_are_converted(self):
        self._post(phone="۰۹۱۲۱۲۳۴۵۶۷")
        self.assertEqual(Order.objects.get().phone, "09121234567")

    def test_bad_phone_shows_a_clear_message(self):
        r = self._post("/en/order/", phone="abc")
        self.assertContains(r, "That phone number doesn", status_code=400)
        self.assertEqual(Order.objects.count(), 0)

    def test_robots_fill_the_hidden_field_and_nothing_is_saved(self):
        r = self._post(website="http://spam.example")
        self.assertRedirects(r, "/fa/order/done/", fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 0)

    def test_same_phone_can_send_three_requests_a_day(self):
        for _ in range(3):
            self.assertEqual(self._post().status_code, 302)
        self.assertEqual(self._post().status_code, 429)
        self.assertEqual(Order.objects.count(), 3)

    def test_one_address_is_limited_to_ten_a_hour(self):
        for _ in range(10):
            self.assertEqual(self._post(phone="bad").status_code, 400)
        self.assertEqual(self._post(phone="bad").status_code, 429)

    def test_opening_the_form_address_directly_goes_home(self):
        r = self.client.get("/fa/order/")
        self.assertRedirects(r, "/fa/#order", fetch_redirect_response=False)

    def test_done_page_needs_a_code_in_the_session(self):
        r = self.client.get("/fa/order/done/")
        self.assertRedirects(r, "/fa/#order", fetch_redirect_response=False)

        session = self.client.session
        session["last_order"] = "141-ABC234"
        session.save()
        r = self.client.get("/fa/order/done/")
        self.assertContains(r, "141-ABC234")
        self.assertContains(r, 'name="robots" content="noindex, nofollow"')

    def test_plan_button_preselects_the_plan_in_the_form(self):
        plan = Plan.objects.create(
            kind="info", level=2, title_fa="هوشمند", title_en="Smart",
            price_fa="x", price_en="x",
        )
        r = self.client.get(f"/fa/?plan={plan.id}")
        self.assertContains(r, f'value="{plan.id}" selected')


class OrderModelTests(TestCase):
    def test_phone_is_masked(self):
        self.assertEqual(Order(phone="09121234567").masked_phone(), "0912***567")


class NotifyTextTests(TestCase):
    def setUp(self):
        self.order = Order(
            name="Sara Karimi", phone="09121234567", code="141-ABC234",
            message="private note", lang="fa",
        )

    @override_settings(TELEGRAM_FULL_DETAILS=False)
    def test_default_message_hides_personal_details(self):
        text = notify.build_text(self.order)
        self.assertIn("141-ABC234", text)
        self.assertIn("0912***567", text)
        for secret in ("Sara", "09121234567", "private note"):
            self.assertNotIn(secret, text)

    @override_settings(TELEGRAM_FULL_DETAILS=True)
    def test_full_details_are_opt_in(self):
        text = notify.build_text(self.order)
        for item in ("Sara Karimi", "09121234567", "private note"):
            self.assertIn(item, text)

    @override_settings(TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="")
    def test_without_a_token_nothing_is_sent(self):
        with patch("orders.notify.threading.Thread") as thread:
            notify.notify_new_order(self.order)
        thread.assert_not_called()


class PurgeCommandTests(TestCase):
    def _order(self, days_old):
        order = Order.objects.create(name="A", phone="09121234567")
        Order.objects.filter(pk=order.pk).update(
            created_at=timezone.now() - timedelta(days=days_old)
        )
        return order

    def test_old_orders_are_deleted(self):
        self._order(400)
        keep = self._order(10)
        call_command("purge_orders", "--days", "365", stdout=io.StringIO())
        self.assertEqual(list(Order.objects.values_list("pk", flat=True)), [keep.pk])

    def test_dry_run_deletes_nothing(self):
        self._order(400)
        out = io.StringIO()
        call_command("purge_orders", "--dry-run", stdout=out)
        self.assertEqual(Order.objects.count(), 1)
        self.assertIn("1 order(s)", out.getvalue())