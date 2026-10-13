from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand

from orders import notify
from orders.models import Order


class Command(BaseCommand):
    help = "Sends a sample order notification through every channel that is turned on. Nothing is saved."

    def handle(self, *args, **options):
        # اطلاعات نمونه است، نه واقعی
        order = Order(
            name="Test Person", phone="09120000000", email="",
            message="This is a test message from notify_test.",
            code="141-TEST22", lang="fa",
        )

        anything = False

        ids = notify.chat_ids()
        if settings.TELEGRAM_BOT_TOKEN and ids:
            anything = True
            text = notify.build_text(order)
            for number, chat_id in enumerate(ids, start=1):
                try:
                    notify.api("sendMessage", {
                        "chat_id": chat_id, "text": text,
                        "parse_mode": "HTML", "disable_web_page_preview": True,
                    })
                    self.stdout.write(f"Telegram: sent to chat {number} ({chat_id})")
                except Exception as exc:
                    self.stdout.write(
                        f"Telegram: failed for chat {number} ({chat_id}): {notify.error_label(exc)}"
                        " - this person probably has not pressed Start on the bot yet"
                    )
        else:
            self.stdout.write("Telegram: not set up (needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID).")

        if notify.email_enabled():
            anything = True
            subject, body = notify.build_email(order)
            try:
                EmailMessage(subject, body, to=list(settings.ORDER_NOTIFY_EMAIL_TO)).send()
                self.stdout.write("Email: sent to " + ", ".join(settings.ORDER_NOTIFY_EMAIL_TO))
            except Exception as exc:
                self.stdout.write(f"Email: failed ({notify.error_label(exc)})")
        else:
            self.stdout.write("Email: not set up (needs EMAIL_HOST and ORDER_NOTIFY_EMAIL_TO). That is fine.")

        if not anything:
            self.stdout.write("\nNothing is turned on yet. Fill in the .env file and run this again.")