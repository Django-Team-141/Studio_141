import io

from django.core.management import call_command
from django.test import TestCase

from portfolio.models import Project


class SeedPortfolioTests(TestCase):
    def test_adds_the_four_projects_once(self):
        call_command("seed_portfolio", stdout=io.StringIO())
        call_command("seed_portfolio", stdout=io.StringIO())
        self.assertEqual(Project.objects.count(), 4)

        p = Project.objects.get(slug="beauty-store")
        self.assertEqual(p.accent, "green")
        self.assertEqual(p.repo_url, "https://github.com/Django-Team-141/beauty-store")

    def test_can_remove_the_old_project_while_adding_the_new_one(self):
        Project.objects.create(title="Online Shop API", slug="online-shop-api", desc_fa="الف", desc_en="a")
        call_command("seed_portfolio", "--remove", "online-shop-api", stdout=io.StringIO())
        self.assertFalse(Project.objects.filter(slug="online-shop-api").exists())
        self.assertTrue(Project.objects.filter(slug="beauty-store").exists())