from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from orders.notify import api


class Command(BaseCommand):
    help = "Finds your Telegram chat id, and with --send sends a test message to the configured chat."

    def add_arguments(self, parser):
        parser.add_argument("--send", action="store_true")

    def handle(self, *args, **opts):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise CommandError("TELEGRAM_BOT_TOKEN is empty in your env file.")

        try:
            updates = api("getUpdates")
        except Exception as exc:
            raise CommandError(f"Could not reach Telegram ({type(exc).__name__}). Is a VPN on?")

        seen = {}
        for u in updates.get("result", []):
            chat = (u.get("message") or u.get("channel_post") or {}).get("chat")
            if chat:
                seen[chat["id"]] = chat.get("type", "?")

        if seen:
            self.stdout.write("Chats that wrote to your bot (put the right one in TELEGRAM_CHAT_ID):")
            for cid, kind in seen.items():
                self.stdout.write(f"  {cid}  ({kind})")
        else:
            self.stdout.write("No messages yet. Open your bot in Telegram, press Start, send 'hi', then run this again.")

        if opts["send"]:
            if not settings.TELEGRAM_CHAT_ID:
                raise CommandError("TELEGRAM_CHAT_ID is empty, so there is nowhere to send.")
            try:
                api("sendMessage", {"chat_id": settings.TELEGRAM_CHAT_ID, "text": "تست: ربات سایت ۱۴۱ وصل است ✅"})
            except Exception as exc:
                raise CommandError(f"Sending failed ({type(exc).__name__}). Check the chat id and that you pressed Start.")
            self.stdout.write("Test message sent.")