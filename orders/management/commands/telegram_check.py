from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from orders.notify import api, chat_ids, error_label


class Command(BaseCommand):
    help = "Lists who wrote to your bot (with their chat numbers), and with --send sends a test message to the configured chats."

    def add_arguments(self, parser):
        parser.add_argument("--send", action="store_true")

    def handle(self, *args, **opts):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise CommandError("TELEGRAM_BOT_TOKEN is empty in your env file.")

        try:
            updates = api("getUpdates")
        except Exception as exc:
            raise CommandError(f"Could not reach Telegram ({error_label(exc)}). Is a VPN on?")

        seen = {}
        for update in updates.get("result", []):
            chat = (update.get("message") or update.get("channel_post") or {}).get("chat")
            if not chat:
                continue
            name = " ".join(x for x in (chat.get("first_name"), chat.get("last_name")) if x) or chat.get("title", "")
            username = chat.get("username")
            seen[chat["id"]] = (chat.get("type", "?"), name, username)

        if seen:
            self.stdout.write("People and chats that wrote to your bot:")
            for cid, (kind, name, username) in seen.items():
                extra = f"  @{username}" if username else ""
                self.stdout.write(f"  {cid}  ({kind})  {name}{extra}")
            self.stdout.write(
                "\nPut each team member's number in TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID_2, _3 or _4. "
                "Only add people you know are on the team."
            )
        else:
            self.stdout.write(
                "No messages yet. Ask each team member to open the bot in Telegram, "
                "press Start and send 'hi', then run this again (with a VPN)."
            )

        if opts["send"]:
            ids = chat_ids()
            if not ids:
                raise CommandError("No chat number is set, so there is nowhere to send.")
            for cid in ids:
                try:
                    api("sendMessage", {"chat_id": cid, "text": "تست: ربات سایت ۱۴۱ وصل است ✅"})
                    self.stdout.write(f"Test message sent to {cid}.")
                except Exception as exc:
                    self.stdout.write(
                        f"Sending to {cid} failed ({error_label(exc)}). "
                        "This person probably has not pressed Start on the bot yet."
                    )