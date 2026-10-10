import secrets

from django.db import models

from plans.models import Plan

# حرف‌هایی که شبیه هم‌اند (0/O، 1/I) در کد نیستند تا موقع تلفنی اشتباه نشود
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def make_code():
    return "141-" + "".join(secrets.choice(ALPHABET) for _ in range(6))


class Order(models.Model):
    STATUSES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("done", "Done"),
        ("cancelled", "Cancelled"),
    ]

    code = models.CharField(max_length=12, unique=True, editable=False)
    name = models.CharField(max_length=80)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    message = models.TextField(max_length=1000, blank=True)
    lang = models.CharField(max_length=2, default="fa", editable=False)
    status = models.CharField(max_length=10, choices=STATUSES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            for _ in range(10):
                candidate = make_code()
                if not Order.objects.filter(code=candidate).exists():
                    self.code = candidate
                    break
        super().save(*args, **kwargs)

    def masked_phone(self):
        p = self.phone
        return p[:4] + "***" + p[-3:] if len(p) >= 9 else "***"