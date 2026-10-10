import base64

import segno
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice


class Command(BaseCommand):
    help = "Sets up 2FA (authenticator app + recovery codes) for an admin user."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--reset", action="store_true", help="replace an existing 2FA setup")

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

        TOTPDevice.objects.filter(user=user).delete()
        StaticDevice.objects.filter(user=user).delete()

        device = TOTPDevice.objects.create(user=user, name="authenticator", confirmed=True)
        secret = base64.b32encode(device.bin_key).decode().rstrip("=")

        self.stdout.write("\nScan this QR code with your authenticator app:\n")
        segno.make(device.config_url).terminal(compact=True)
        self.stdout.write("If the QR is garbled, add it by hand ('enter a setup key'):")
        self.stdout.write("  " + secret + "\n")

        static = StaticDevice.objects.create(user=user, name="recovery", confirmed=True)
        codes = []
        for _ in range(8):
            token = StaticToken.random_token()
            StaticToken.objects.create(device=static, token=token)
            codes.append(token)

        self.stdout.write("Recovery codes (each works once, shown only now). Put them in your password manager:")
        for c in codes:
            self.stdout.write("  " + c)
        self.stdout.write("\nDone. Clear this terminal (cls) so the secret does not stay on screen.")