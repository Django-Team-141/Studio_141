from django.db import models


class Plan(models.Model):
    KINDS = [
        ("info", "Personal / company site"),
        ("shop", "Online store"),
    ]
    LEVELS = [
        (1, "Basic"),
        (2, "Smart"),
        (3, "Custom"),
    ]

    kind = models.CharField(max_length=4, choices=KINDS)
    level = models.PositiveSmallIntegerField(choices=LEVELS)
    title_fa = models.CharField(max_length=60)
    title_en = models.CharField(max_length=60)
    price_fa = models.CharField(max_length=40, help_text="e.g. از ۱۵ میلیون تومان")
    price_en = models.CharField(max_length=40, help_text="e.g. from $400")
    is_featured = models.BooleanField(default=False, help_text="Highlights the card (usually the Smart plan).")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["level"]
        constraints = [
            models.UniqueConstraint(fields=["kind", "level"], name="one_plan_per_kind_and_level"),
        ]

    def __str__(self):
        return f"{self.get_kind_display()} · {self.title_en}"


class PlanFeature(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="features")
    text_fa = models.CharField(max_length=120)
    text_en = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text_en