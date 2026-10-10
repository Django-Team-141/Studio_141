from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Order


class Command(BaseCommand):
    help = "Deletes orders older than N days (default 365). Use --dry-run to only count them."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=365)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options["days"])
        old = Order.objects.filter(created_at__lt=cutoff)
        count = old.count()

        if options["dry_run"]:
            self.stdout.write(f"{count} order(s) older than {options['days']} days would be deleted.")
            return

        old.delete()
        self.stdout.write(f"Deleted {count} order(s) older than {options['days']} days.")