import base64
import os
import re
import sys
from pathlib import Path

import segno
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice


def safe_name(username):
    """اسم کاربری را برای اسم فایل امن می‌کند."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", username) or "user"


class Command(BaseCommand):
    help = "Sets up 2FA (authenticator app + recovery codes) for an admin user."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--reset", action="store_true", help="replace an existing 2FA setup")
        parser.add_argument(
            "--terminal", action="store_true",
            help="show the QR code and the recovery codes in the terminal and save no files (use this on a server)",
        )
        parser.add_argument(
            "--no-open", action="store_true",
            help="do not open the QR image and do not wait for Enter",
        )

    def handle(self, *args, **opts):
        User = get_user_model()
        try:
            user = User.objects.get(**{User.USERNAME_FIELD: opts["username"]})
        except User.DoesNotExist:
            raise CommandError("There is no user with that username.")
        if not user.is_staff:
            raise CommandError("This user is not staff, so there is nothing to protect.")

        if TOTPDevice.objects.filter(user=user).exists() and not opts["reset"]:
            raise CommandError("2FA is already set up for this user. Add --reset to replace it.")

        files = None
        try:
            # اگر نوشتن فایل‌ها خطا بدهد، همه‌ی تغییرهای دیتابیس برمی‌گردد
            # و حساب با تنظیمات قبلی‌اش می‌ماند.
            with transaction.atomic():
                TOTPDevice.objects.filter(user=user).delete()
                StaticDevice.objects.filter(user=user).delete()

                device = TOTPDevice.objects.create(user=user, name="authenticator", confirmed=True)
                static = StaticDevice.objects.create(user=user, name="recovery", confirmed=True)
                codes = []
                for _ in range(8):
                    token = StaticToken.random_token()
                    StaticToken.objects.create(device=static, token=token)
                    codes.append(token)

                if not opts["terminal"]:
                    files = self._write_files(user, device, codes)
        except OSError as exc:
            raise CommandError(f"Could not save the files, so nothing was changed: {exc}")

        if opts["terminal"]:
            self._show_in_terminal(device, codes)
        else:
            self._after_files(files, opts["no_open"])

    # ---------- حالت فایل (روی سیستم خودتان) ----------

    def _write_files(self, user, device, codes):
        out_dir = Path(getattr(settings, "TWO_FA_OUTPUT_DIR", settings.BASE_DIR / "2fa_codes"))
        out_dir.mkdir(parents=True, exist_ok=True)

        name = safe_name(user.get_username())
        png = out_dir / f"{name}-qr.png"
        txt = out_dir / f"{name}-recovery-codes.txt"

        try:
            segno.make(device.config_url).save(str(png), scale=8, border=4)

            stamp = timezone.localtime().strftime("%Y-%m-%d %H:%M")
            lines = [
                f"کدهای بازیابی ۲FA برای کاربر: {user.get_username()}",
                f"ساخته‌شده در: {stamp}",
                "هر کد فقط یک بار کار می‌کند. وقتی گوشی یا اپ احراز هویتتان در دسترس نبود،",
                "یکی از این‌ها را به‌جای کد شش‌رقمی وارد کنید.",
                "",
                *codes,
                "",
                "این کدها را داخل password manager بگذارید و بعد همین فایل را پاک کنید.",
                "این فایل را در گیت، چت یا ایمیل نگذارید.",
            ]
            txt.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")

            for path in (png, txt):
                try:
                    os.chmod(path, 0o600)
                except OSError:
                    pass
        except OSError:
            for path in (png, txt):
                path.unlink(missing_ok=True)
            raise

        return png, txt

    def _after_files(self, files, no_open):
        png, txt = files
        self.stdout.write("")
        self.stdout.write("QR image:       " + str(png))
        self.stdout.write("Recovery codes: " + str(txt))
        if no_open:
            return

        if os.name == "nt":
            try:
                os.startfile(str(png))
            except OSError:
                self.stdout.write("Could not open the image by itself. Open the file above yourself.")

        if sys.stdin.isatty():
            input("\nScan the QR code with your authenticator app, then press Enter to delete the image... ")
            png.unlink(missing_ok=True)
            self.stdout.write("The QR image was deleted.")
        else:
            self.stdout.write("Delete the QR image yourself after you scan it.")

        self.stdout.write("Put the recovery codes in your password manager, then delete the text file.")

    # ---------- حالت ترمینال (روی سرور) ----------

    def _show_in_terminal(self, device, codes):
        secret = base64.b32encode(device.bin_key).decode().rstrip("=")

        self.stdout.write("\nScan this QR code with your authenticator app:\n")
        segno.make(device.config_url).terminal(compact=True)
        self.stdout.write("If the QR is garbled, add it by hand ('enter a setup key'):")
        self.stdout.write("  " + secret + "\n")

        self.stdout.write("Recovery codes (each works once, shown only now). Put them in your password manager:")
        for code in codes:
            self.stdout.write("  " + code)
        self.stdout.write("\nDone. Clear this terminal so the secret does not stay on screen.")