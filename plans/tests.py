from types import SimpleNamespace

from django.db import IntegrityError, transaction
from django.test import TestCase

from plans.models import Plan, PlanFeature
from plans.templatetags.plans_tags import _rows


def card(features, includes_lower=True):
    return {"p": SimpleNamespace(includes_lower=includes_lower), "features": features}


class ComparisonRowsTests(TestCase):
    def test_each_plan_has_what_the_lower_plans_have(self):
        cards = [card(["A"]), card(["B"]), card(["C"])]
        rows = {r["text"]: r["cells"] for r in _rows(cards)}
        self.assertEqual(rows["A"], [True, True, True])
        self.assertEqual(rows["B"], [False, True, True])
        self.assertEqual(rows["C"], [False, False, True])

    def test_a_plan_that_does_not_include_the_lower_one(self):
        cards = [card(["A"]), card(["B"]), card(["C"], includes_lower=False)]
        rows = {r["text"]: r["cells"] for r in _rows(cards)}
        self.assertEqual(rows["A"], [True, True, False])
        self.assertEqual(rows["B"], [False, True, False])
        self.assertEqual(rows["C"], [False, False, True])


class PlansPageTests(TestCase):
    def test_comparison_table_is_built_from_features(self):
        a = Plan.objects.create(
            kind="info", level=1, title_fa="پایه", title_en="Basic", price_fa="x", price_en="x",
        )
        b = Plan.objects.create(
            kind="info", level=2, title_fa="هوشمند", title_en="Smart",
            price_fa="y", price_en="y", is_featured=True,
        )
        PlanFeature.objects.create(plan=a, text_fa="الف", text_en="Contact form")
        PlanFeature.objects.create(plan=b, text_fa="ب", text_en="Blog")
        r = self.client.get("/en/")
        self.assertContains(r, "Compare the plans")
        self.assertContains(r, 'class="cmp"')

    def test_one_plan_per_kind_and_level(self):
        Plan.objects.create(
            kind="info", level=1, title_fa="الف", title_en="A", price_fa="x", price_en="x",
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Plan.objects.create(
                    kind="info", level=1, title_fa="ب", title_en="B", price_fa="x", price_en="x",
                )